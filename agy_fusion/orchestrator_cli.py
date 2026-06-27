import asyncio
import subprocess
import os
from tlb_cli import tlb
from config import MODEL_SONNET, MODEL_OPUS, MODEL_GEMINI_PRO, MODEL_GEMINI_FLASH
from ui import run_with_spinner, print_header, print_success, print_error, print_warning, print_step, Colors

# Phase 1: Assessor Prompt
ASSESSOR_PROMPT = """You are a highly efficient Project Manager (Gemini 3.5 Flash).
Analyze the following user request and determine its technical difficulty and complexity.
If the task involves major architectural changes, extreme edge cases, complex algorithms, or high concurrency, classify it as HARD.
If the task is a standard implementation, refactoring, or straightforward feature addition, classify it as NORMAL.

You MUST output your final decision enclosed in XML tags exactly like this:
<difficulty>HARD</difficulty>
or
<difficulty>NORMAL</difficulty>

Request: {request}
"""

# Phase 2: Deliberator Prompts
PRO_PROMPT = """You are a world-class Staff Software Engineer (Gemini 3.1 Pro).
Analyze the request and provide a deep, structurally sound architectural proposal. Focus on code maintainability and systemic design.
IMPORTANT: DO NOT WRITE ANY CODE. Output ONLY high-level architectural design, logic flow, and structural plans in plain text/markdown. Writing actual code is STRICTLY FORBIDDEN to save tokens.

Your output MUST be structured EXACTLY with the following Markdown headers:
# 1. Architecture & Components
# 2. Data Flow & Interfaces
# 3. Edge Cases & Mitigation

Request: {request}"""

SONNET_PROMPT = """You are a pragmatic, fast software architect (Claude 4.6 Sonnet).
Analyze the request and provide a clear, standard implementation strategy. Focus on rapid delivery and modern best practices.
IMPORTANT: DO NOT WRITE ANY CODE. Output ONLY high-level architectural design, logic flow, and structural plans in plain text/markdown. Writing actual code is STRICTLY FORBIDDEN to save tokens.

Your output MUST be structured EXACTLY with the following Markdown headers:
# 1. Architecture & Components
# 2. Data Flow & Interfaces
# 3. Edge Cases & Mitigation

Request: {request}"""

OPUS_PROMPT = """You are a world-class principal engineer (Claude 4.8 Opus).
Analyze the request focusing on the hardest edge cases, performance bottlenecks, and concurrency issues. Provide a highly resilient architecture.
IMPORTANT: DO NOT WRITE ANY CODE. Output ONLY high-level architectural design, logic flow, and structural plans in plain text/markdown. Writing actual code is STRICTLY FORBIDDEN to save tokens.

Your output MUST be structured EXACTLY with the following Markdown headers:
# 1. Architecture & Components
# 2. Data Flow & Interfaces
# 3. Edge Cases & Mitigation

Request: {request}"""

# Phase 3: Judge Prompt
JUDGE_PROMPT = """You are the Supreme Judge and Chief Architect (Gemini 3.1 Pro).
Review the two architectural proposals from your senior engineers regarding the user's request.
Synthesize the best parts, resolve contradictions, and output the absolute, final, perfect 'Ultimate Implementation Blueprint'.

Your output MUST be structured EXACTLY with the following Markdown headers for easy parsing:
# Overall Architecture
(Explain the merged vision here)

# Component Breakdown
(List each logical component)

# File-by-File Blueprint
(Detail the exact file paths and the responsibilities of each file)

IMPORTANT: Do NOT write the final executable code yet. Output ONLY the architectural layout and detailed design. Writing code is STRICTLY FORBIDDEN to save tokens.

Original Request: {request}

--- PROPOSAL 1 (Gemini 3.1 Pro) ---
{prop1}

--- PROPOSAL 2 (Claude) ---
{prop2}
"""

# Phase 4: Coder Prompt
CODER_PROMPT = """You are an elite Lead Programmer (Gemini 3.5 Flash).
You have been given the 'Ultimate Implementation Blueprint' by the Chief Architect.
Your job is to read this blueprint and write the final, perfect, production-ready code.

You MUST generate the complete, robust code. 
CRITICAL RULE: For every file you write, you MUST wrap the content in a Markdown code block, and the very first line inside the code block MUST be a comment with the exact file path (e.g. `# filepath: src/main.py` or `// filepath: src/main.js`). This format is strictly required for auto-parsing.

DO NOT leave placeholder functions or "TODOs". Write the actual logic.

Original Request: {request}

--- ULTIMATE BLUEPRINT ---
{blueprint}

Output the final code and file structures.
"""

async def run_agy_cli(prompt: str, model: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        config = tlb.get_active_config()
        agy_bin = config["bin"]
        fake_home = config["home"]
        
        env = os.environ.copy()
        env["HOME"] = fake_home
        
        # Dangerously skip permissions to avoid CLI waiting for stdin confirmations
        cmd = [agy_bin, "--dangerously-skip-permissions", "--model", model, "-p", prompt]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        out_str = stdout.decode('utf-8')
        err_str = stderr.decode('utf-8')
        
        if process.returncode == 0:
            return out_str
        else:
            err_lower = err_str.lower()
            if "limit exceeded" in err_lower or "quota" in err_lower or " 429 " in err_lower or "status: 429" in err_lower or "http 429" in err_lower:
                print_warning(f"\nRate limit hit on {os.path.basename(fake_home)}. Rotating account...")
                tlb.mark_exhausted(config)
            else:
                raise Exception(f"agy CLI failed: {err_str}")
            
            await asyncio.sleep(2 ** attempt)
            continue

    raise Exception(f"Failed to call agy CLI after {max_retries} retries due to limits.")

async def run_fusion(task_description: str):
    print_header("PHASE 1: Difficulty Assessment")
    assessor_prompt = ASSESSOR_PROMPT.format(request=task_description)
    try:
        assessment_res = await run_with_spinner("Analyzing complexity with Gemini 3.5 Flash", run_agy_cli(assessor_prompt, MODEL_GEMINI_FLASH))
        is_hard = "<DIFFICULTY>HARD</DIFFICULTY>" in assessment_res.upper()
    except Exception as e:
        print_warning(f"Assessment failed, falling back to NORMAL: {e}")
        is_hard = False
        
    difficulty_label = "HARD (Routing to Opus)" if is_hard else "NORMAL (Routing to Sonnet)"
    print_step(f"Determined Difficulty: {Colors.BOLD}{difficulty_label}{Colors.RESET}")

    print_header("PHASE 2: Parallel Deliberation")
    pro_prompt = PRO_PROMPT.format(request=task_description)
    
    # We create the tasks but wait for them together
    async def deliberate():
        pro_task = asyncio.create_task(run_agy_cli(pro_prompt, MODEL_GEMINI_PRO))
        if is_hard:
            claude_task = asyncio.create_task(run_agy_cli(OPUS_PROMPT.format(request=task_description), MODEL_OPUS))
        else:
            claude_task = asyncio.create_task(run_agy_cli(SONNET_PROMPT.format(request=task_description), MODEL_SONNET))
            
        return await asyncio.gather(pro_task, claude_task, return_exceptions=True)

    results = await run_with_spinner("Generating dual architectural proposals (Pro & Claude)", deliberate())
    
    if isinstance(results[0], Exception) or isinstance(results[1], Exception):
        print_error(f"One or both architects failed. Pro: {results[0]}, Claude: {results[1]}")
        return None
    
    pro_res, claude_res = results
        
    print_header("PHASE 3: Ultimate Judgment")
    judge_prompt = JUDGE_PROMPT.format(
        request=task_description,
        prop1=pro_res,
        prop2=claude_res
    )
    
    try:
        blueprint = await run_with_spinner("Synthesizing Ultimate Blueprint (Gemini 3.1 Pro)", run_agy_cli(judge_prompt, MODEL_GEMINI_PRO))
    except Exception as e:
        print_error(f"Judgment failed: {e}")
        return None

    print_header("PHASE 4: Final Code Generation")
    coder_prompt = CODER_PROMPT.format(request=task_description, blueprint=blueprint)
    
    try:
        final_code = await run_with_spinner("Drafting production code (Gemini 3.5 Flash)", run_agy_cli(coder_prompt, MODEL_GEMINI_FLASH))
        print_success("\nFusion processing successfully completed!")
        return final_code
    except Exception as e:
        print_error(f"Code Generation failed: {e}")
        return None
