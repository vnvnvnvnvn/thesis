#!/usr/bin/env python

import pickle
import re

conditions = r"(a|ae|b|be|c|e|g|ge|l|le|na|nae|nb|nbe|nc|ne|ng|nge|nl|nle|no|np|ns|nz|o|p|pe|po|s|z)?"
suffix = r"(b|d|q|w|l)?"
packed = r"(pd|ps|sd|ss)?"
opcode_classify = {
    r"^j" + conditions + r"$": "BRANCH",
    r"^(jmp|jcxz|jecxz|jrcxz|ljmp)" + suffix + r"$": "BRANCH",
    r"(f)?cmov" + conditions + suffix + r"$": "TRANSFER",
    r".?mov(s)?" + suffix: "TRANSFER",
    r"(lod|sto)(s)?" + suffix: "TRANSFER",
    r".?(and|andn|clc|cld|cli|cmc|neg|not|or|stc|std|sti|test|xor)" + suffix: "LOGICAL",
    r"^set" + conditions + r"$": "LOGICAL",
    r"(in|ins|outs|lahf|lds|lea|les|out|pop|popf|push|pushf|sahf|popa|pusha)" + suffix + r"$": "TRANSFER",
    r".*(aaa|aad|aam|aas|adc|add|cmp|daa|das|dec|div|idiv|imul|inc|mul|rcl|rcr|rol|ror|sal|sar|shl|shr|sub|sbb)" + suffix + packed: "ARITHMETIC",
    r".*(min|max|abs|sad|sqrt|sca)": "ARITHMETIC",
    r"loop" + conditions + r"$": "PROC",
    r"rep" + conditions + r"$": "PROC",
    r"(call|callq|int|iret|nop|fnop|ret|retn|retf|wait|xchg|xlat|hlt|lock)": "PROC",
    r"(bound|enter|leave|inv|bnd)": "PROC",
    r"(lar|lgdt|lidt|lldt|lmsw|lsl|ltr|sgdt|sidt|sldt|smsw|str)": "TRANSFER",
    r"(cbw|cwd)" + r"$": "LOGICAL",
    r"(rsm|syscall|sysenter|sysexit|sysret)": "PROC",
    r"(cvt|vcvt|vget|vpmov|ftst|stac)": "LOGICAL",
    r".?(pack|unpck)": "TRANSFER",
    r".*blend": "LOGICAL",
    r"(aes|sha|gf2|kshift|vreduce)": "ARITHMETIC",
    r"(esc)" + r"$": "COPROC",
    r".*round": "ARITHMETIC",
    r"(bsf|bsr|bt|btc|btr|bts|cdq|cwde|ibts|bswap|cdqe|cqo|bextr|vptest|scas)": "LOGICAL",
    r"(bndldx|bndstx|fbld|fbstp|fild|fist|fld|fns|fsave|fxch|fst|lddqu|ldmxcsr|lfence|lfs|lgs|lss|maskmov|sfence|stmxcsr)": "TRANSFER",
    r"(comisd|comiss|fcom|fcomi|fcomip|fcomp|fcompp|ficom|ficomp|fucom|fucomi|fucomip|fucomp|fucompp|ucomisd|ucomiss)": "ARITHMETIC",
    r"v(p)?(expand|maskmov|compress)": "TRANSFER",
    r"(pins|blsi|fxtract|pext|xgetbv|xsetbv)": "TRANSFER",
    r"(v|vp)*(gather|extract|insert)": "TRANSFER",
    r"(v|vp|p)*(perm|scatter|scale|shuf|rcp|fixup|range)": "ARITHMETIC",
    r"(psll|psra|psrl|vpsll|vpsra|vpsrl|vrnd|vplzcnt|vpconflict|lzcnt|tzcnt|vzero|palign|pdep|valign)": "ARITHMETIC",
    r"u?(monitor|mwait)": "PROC",
    r"(arpl|clts|verr|verw|frstor|fxrstor|xrstor|xrstors|xsave|fclex|ffree|finit|fnclex|fninit|fwait|fxsave)": "PROC",
    r"(fxam|kxnor|vfpclass|vptern|psign|vpsign)": "LOGICAL",
    r"(f2xm1|fchs|fcos|fpatan|fprem|fprem1|fptan|frndint|fscale|fsin|fyl2x|fyl2xp1|adox|pavg|popcnt|crc32|dpp)": "ARITHMETIC",
    r"(xabort|xacquire|xbegin|xend|xlatb|xrelease|prefet|tpause|pause|cpuid|clflush|clwb|emms|mfence|ptwrite|swapgs)": "PROC",
    r"(wbinvd|wr|rd)": "TRANSFER",
    r"(blsmsk|blsr|bzhi|clac)": "LOGICAL"
}

unmatched = []
record_type = {}
def classify(instr):
    matched = False
    instr_lower = instr.lower()
    for template, t in opcode_classify.items():
        if re.match(template, instr_lower):
            matched = True
            record_type[instr_lower] = t
            # print(instr_lower + ":" + t)
            break
    if not matched:
        unmatched.append(instr)
    return matched

if __name__=='__main__':
    with open('core_x86.pkl', 'r') as f:
        data = pickle.load(f)
        for d, e in data.items():
            m = classify(d)
    print(len(unmatched))
    unmatched = sorted(unmatched)
    print(unmatched)
    pck = []
    for u in unmatched:
        #if re.match(r"^s", u.lower()):
        print(u+":"+data[u])
        pck.append(u.lower())
    print(len(pck))
    print("|".join(pck))
    print(record_type['fnstcw'])
