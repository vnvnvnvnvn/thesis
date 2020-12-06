#!/usr/bin/env python3

import re
from collections import defaultdict

class InstructionSimplifier(object):
    def __init__(self):
        self.simplifiers = {}
        self.simplifiers['x86'] = self.X86()
        self.simplifiers['arm'] = self.Arm()

    def simplify(self, block, arch, jmp_pts=set()):
        sim_block = [self.simplifiers[arch].simplify(instruction, jmp_pts)
                     for instruction in block]
        return sim_block

    def conclude(self):
        print(self.simplifiers['x86'].notrecognized)
        print(self.simplifiers['x86'].opcode)
        print(self.simplifiers['x86'].opcode_matched)
        print(self.simplifiers['x86'].code_counter)
        print(self.simplifiers['arm'].opcode)
        print(self.simplifiers['arm'].opcode_matched)
        print(self.simplifiers['arm'].code_counter)

    class X86(object):
        def __init__(self):
            self.notrecognized = set()
            self.opcode = set()
            self.opcode_matched = set()
            self.code_counter = defaultdict(lambda: 0)
            conditions = r"(a|ae|b|be|c|e|g|ge|l|le|na|nae|nb|nbe|nc|ne|ng|nge|nl|nle|no|np|ns|nz|o|p|pe|po|s|z)?"
            suffix = r"(b|d|q|w|l)?"
            packed = r"(pd|ps|sd|ss)?"
            self.opcode_classify = {
                r"^j" + conditions + r"$": "BRANCH",
                r"^(jmp|jcxz|jecxz|jrcxz|ljmp)" + suffix + r"$": "BRANCH",
                r"(f)?cmov" + conditions + suffix + r"$": "TRANSFER",
                r".?mov(s)?" + suffix: "TRANSFER",
                r"(lod|sto)(s)?" + suffix: "TRANSFER",
                r".?(and|andn|clc|cld|cli|cmc|neg|not|or|stc|std|sti|test|xor)" + suffix: "LOGICAL",
                r"^set" + conditions + r"$": "LOGICAL",
                r"(in|ins|outs|lahf|lds|lea|les|out|pop|popf|push|pushf|sahf|popa|pusha|clt)" + suffix + r"$": "TRANSFER",
                r".*(aaa|aad|aam|aas|adc|add|cmp|daa|das|dec|div|idiv|imul|inc|mul|rcl|rcr|rol|ror|sal|sar|shl|shr|sub|sbb)" + suffix + packed: "ARITHMETIC",
                r".*(min|max|abs|sad|sqrt|sca)": "ARITHMETIC",
                r"loop" + conditions + r"$": "PROC",
                r"rep" + conditions: "PROC",
                r"(call|callq|int|iret|nop|fnop|ret|retn|retf|wait|xchg|xlat|hlt|lock)": "PROC",
                r"(bound|enter|leave|inv|bnd)": "PROC",
                r"(lar|lgdt|lidt|lldt|lmsw|lsl|ltr|sgdt|sidt|sldt|smsw|str)": "TRANSFER",
                r"(cbw|cwd|cwtl|cqto)" + r"$": "LOGICAL",
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
                r"(xabort|xacquire|xbegin|xend|xlatb|xrelease|prefet|tpause|pause|cpuid|clflush|clwb|emms|femms|mfence|ptwrite|swapgs)": "PROC",
                r"(wbinvd|wr|rd)": "TRANSFER",
                r"(blsmsk|blsr|bzhi|clac)": "LOGICAL"
            }
            self.word_size = set(["word", "dword", "byte", "qword", "xmmword", "ptr"])

        def remove_extra(self, instr):
            instr = re.sub(r"#.+", "", instr)
            instr = instr.replace(",", " ")
            instr = instr.replace(":", " ")
            instr = instr.replace("!", " ")
            instr = instr.split()
            for i in range(len(instr)):
                if instr[i] in self.word_size:
                    instr[i] = ""
            instr = " ".join(instr)
            return instr

        def immediate(self, instr):
            instr = re.sub(r"\b[\-]?[0-9]+\b", 'IMM', instr)
            instr = re.sub(r"\b0x[\-]?[0-9abcdef]+\b", 'IMM', instr)
            return instr

        def address(self, instr):
            return re.sub(r"[^[\s]*\[.+\]", "ADDR", instr)

        def bb_label(self, instr, remaining, jmp_pts):
            if not re.match(r"(call|j)", instr):
                return remaining
            instr_split = remaining.split()
            for i in range(len(instr_split)):
                if instr_split[i] in jmp_pts:
                    instr_split[i] = "BB"
                else:
                    instr_split[i] = "FUNC"
            instr = " ".join(instr_split)
            return instr

        def reg_class(self, instr):
            regs = [r"[re]?[abcd]x\b",
                    r"[abcd][lh]\b",
                    r"[re]?[sd]i\b",
                    r"[sd]il\b",
                    r"[x]?mm[0-9]+\b",
                    r"r[0-9]+[dwb]?\b"]
            reg_pointer = r"(rbp|rsp|ebp|esp|bp|sp)[lh]?\b"
            for r in regs:
                instr = re.sub(r, "REG", instr)
            return re.sub(reg_pointer, "REGPTR", instr)

        def variable(self, instr):
            il = instr.split()
            for idx, part in enumerate(il):
                if part not in set(["VAR", "IMM", "ADDR", "FUNC", "BB", "REG", "REGPTR"]):
                    self.notrecognized.add(il[idx])
                    il[idx] = "VAR"
            return " ".join(il)

        def classify(self, instr):
            matched = False
            for template, t in self.opcode_classify.items():
                if re.match(template, instr):
                    matched = True
                    self.code_counter[t] += 1
                    self.opcode_matched.add(instr)
                    return t
            if not matched:
                self.opcode.add(part)
            return instr

        def simplify(self, instr, jmp_pts=set()):
            s = instr.split(" ", 1)
            if len(s) > 1:
                instr, remaining_part = s
                remaining_part = self.remove_extra(remaining_part)
                remaining_part = self.address(remaining_part)
                remaining_part = self.bb_label(instr, remaining_part, jmp_pts)
                remaining_part = self.immediate(remaining_part)
                remaining_part = self.reg_class(remaining_part)
                remaining_part = self.variable(remaining_part)
            else:
                instr = s[0]
                remaining_part = ""
            instr = self.classify(instr)
            return " ".join([instr, remaining_part])

    class Arm(object):
        def __init__(self):
            self.opcode = set()
            self.opcode_matched = set()
            self.code_counter = defaultdict(lambda: 0)
            self.flags = r"(al|eq|ne|cs|cc|hs|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)?"
            logic = r"(and|eor|orr|orn|neg|bic|tst|teq|mov|mov32|movt|mvn|clz|bfc|bfi|clrex|pkhbt|pkhtb|sbfx|sel|ssat|ssat16|ubfx|usat|usat16)"
            arithmetic = r"(sub|rsb|add|adc|sbc|rsc|cmp|cmn|lsl|lsr|asr|ror|rrx|subs|usad8|usada8|usad16)"
            multiply = r"(mul|mla|mls|mull|mlal|umull|smull|umlal|smlal|sdiv|smlald|udiv|umaal|umull)"
            self.opcode_classify = {
                r"(b|bl|bx|blx|bxj|cbz|cbnz)" + self.flags + "(\.w)?$": "BRANCH",
                logic + self.flags + r"[s]?$": "LOGICAL",
                logic + r"[s]?" + self.flags + "$": "LOGICAL",
                arithmetic + self.flags + r"[s]?$": "ARITHMETIC",
                arithmetic + r"[s]?" + self.flags + "$": "ARITHMETIC",
                multiply + self.flags + r"[s]?$": "ARITHMETIC",
                multiply + r"[s]?" + self.flags + r"$": "ARITHMETIC",
                r"(u|s)xt(ab|ab16|ah|b|h|b16)" + self.flags + r"$": "ARITHMETIC",
                r"(smla|smlal|smul)(b|t)(b|t)" + self.flags + r"$": "ARITHMETIC",
                r"(smlaw|smulw)(b|t)" + self.flags + r"$": "ARITHMETIC",
                r"(smlsd|smlsld|smmla|smmls|smmul|smuad|smusd)"
                r"q(d)?(add|sub)(8|16)?" + self.flags + r"$": "ARITHMETIC",
                r"(s|u|uq)(h)?(add|sub)(8|16)?" + self.flags + r"$": "ARITHMETIC",
                r"(s|u|uq)(h)?sax" + self.flags + r"$": "ARITHMETIC",
                r"(qasx|qsax|rbit|rev|rev16|revsh)" + self.flags + r"$": "ARITHMETIC",
                r"(ldr|str)" + self.flags + r"[b]?[t]?$": "TRANSFER",
                r"(ldr|str)" + self.flags + r"(h|sh|sb)$": "TRANSFER",
                r"(ldr|str|ldrex|strex)(d|b|h|sh|sb)?" + self.flags + r"(\.w)?$": "TRANSFER",
                r"(pop|push|cpy)" + self.flags + r"$": "TRANSFER",
                r"(adr|adrl)" + self.flags + r"(\.w)?": "TRANSFER",
                r"(msr|mrs|pld)" + self.flags + r"$": "TRANSFER",
                r"(ldm|stm)" + self.flags + r"(fd|ed|fa|ea|ia|ib|da|db)?" + r"$": "TRANSFER",
                r"(ldm|stm|srs)(fd|ed|fa|ea|ia|ib|da|db)?" + self.flags + r"$": "TRANSFER",
                r"swp" + self.flags + r"[b]?$": "TRANSFER",
                r"cps(ie|id)?": "PROC",
                r"(nop|dbg|dmb|dsb|eret|hvc|isb|pld|pli|pldw|rfe)" + self.flags + r"$": "PROC",
                r"(swi|bkpt|setend|sev|smc|svc|tbb|tbh|wfe|wfi|yield)" + self.flags + r"$": "PROC",
                r"(cdp|ldc|stc|mcr|mrc|cdp2|ldc2|mcr2|mcrr|mcrr2|mrc2|mrrc|stc2|sys)" + self.flags + r"[l]?$": "COPROC"
            }

        def remove_extra(self, instr):
            instr = re.sub(r"@.+", "", instr)
            instr = re.sub(',', " ", instr)
            instr = re.sub('{', " ", instr)
            instr = re.sub('}', " ", instr)
            return instr

        def immediate(self, instr):
            return re.sub(r"#[\-]?[0-9]+\b", "IMM", instr)

        def address(self, instr):
            return re.sub(r"\[.+\][!]?", "ADDR", instr)

        def function(self, instr):
            instr = re.sub(r"bl\s.+", "bl FUNC", instr)
            return re.sub(r"^b[\s]+[\w]+", "b FUNC", instr)

        def bb_label(self, instr):
            return re.sub(r"\.LBB[^\s]+", "BB", instr)

        def reg_class(self, instr):
            regs = r"-?r[0-9]+!?"
            reg_pointer = r"(pc|sp|lr)!?"
            instr = re.sub(regs, "REG", instr)
            instr = re.sub(reg_pointer, "REGPTR", instr)
            instr = re.sub(reg_pointer, "REG", instr)
            return instr

        def variable(self, instr):
            instr = re.sub(r"\.LCPI[^\s]+", "VAR", instr)
            instr = re.sub(r"\.LJTI[^\s]+", "VAR", instr)
            return re.sub(r"-?\d+\b", "VAR", instr)

        def classify(self, instr):
            il = instr.split()
            for idx, part in enumerate(il):
                matched = False
                if part not in ["VAR", "IMM", "ADDR", "FUNC", "BB", "REG", "REGPTR"]:
                    for template, t in self.opcode_classify.items():
                        if re.match(template, part):
                            matched = True
                            il[idx] = t
                            self.code_counter[t] += 1
                            self.opcode_matched.add(part)
                    if not matched:
                        il[idx] = "VAR"
                        self.opcode.add(part)
            return " ".join(il[:3])

        def simplify(self, instr):
            instr = self.remove_extra(instr)
            instr = self.immediate(instr)
            instr = self.address(instr)
            instr = self.function(instr)
            instr = self.bb_label(instr)
            instr = self.reg_class(instr)
            instr = self.variable(instr)
            instr = self.classify(instr)
            return instr
