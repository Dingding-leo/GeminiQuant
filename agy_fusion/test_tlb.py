import asyncio
from tlb_cli import tlb

def test():
    tlb.init_db()
    c1 = tlb.get_active_config()
    print("Config 1:", c1)
    tlb.mark_exhausted(c1)
    
    c2 = tlb.get_active_config()
    print("Config 2:", c2)
    tlb.mark_exhausted(c2)
    
    c3 = tlb.get_active_config()
    print("Config 3:", c3)
    tlb.mark_exhausted(c3)
    
    try:
        c4 = tlb.get_active_config()
        print("Config 4:", c4)
    except Exception as e:
        print("Exception caught correctly when all exhausted:", e)

if __name__ == "__main__":
    test()
