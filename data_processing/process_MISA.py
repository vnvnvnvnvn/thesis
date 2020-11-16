#!/usr/bin/env python

import re
from collections import defaultdict

class InstructionSimplifier(object):
    def __init__(self):
        self.simplifiers = {}
        self.simplifiers['x86'] = self.X86()
        self.simplifiers['arm'] = self.Arm()

    def simplify(self, block, arch):
        sim_block = [self.simplifiers[arch].simplify(instruction)
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
            conditions = r"(a|ae|b|be|c|e|g|ge|l|le|na|nae|nb|nbe|nc|ne|ng|nge|nl|nle|no|np|ns|nz|o|p|pe|po|s|z)"
            suffix = r"(b|d|q|w|l)?"
            packed = r"(pd|ps|sd|ss)?"
            self.opcode_classify = {
                r"^j" + conditions + r"$": "BRANCH",
                r"^(jmp|jcxz|jecxz|jrcxz|ljmp)" + suffix + r"$": "BRANCH",
                r"(f)?cmov" + conditions + suffix + r"$": "TRANSFER",
                r"mov(s)?" + suffix: "TRANSFER",
                r"(and|clc|cld|cli|cmc|neg|not|or|stc|std|sti|test|xor|bsf|bsr|bt|btc|btr|bts|cdq|cwde|ibts|bswap|cdqe|cqo|bextr)" + suffix + r"$": "LOGICAL",
                r"^set" + conditions + r"$": "LOGICAL",
                r"(aaa|aad|aam|aas|adc|add|cmp|cmpsb|cmpsw|daa|das|dec|div|idiv|imul|inc|mul|rcl|rcr|rol|ror|sal|sar|scasb|scasw|shl|shr|sub|sbb)" + suffix + packed: "ARITHMETIC",
                r"loop" + conditions + r"$": "PROC",
                r"(callq|int|into|iret|nop|ret|retn|retf|wait|xchg|xlat|hlt|lock)$": "PROC",
                r"(in|lahf|lds|lea|les|lodsb|lodsw|out|pop|popf|push|pushf|sahf|stosb|stosw)" + suffix + r"$": "TRANSFER"
            }
        def remove_extra(self, instr):
            instr = re.sub(r"#.+", "", instr)
            instr = instr.replace(",", " ")
            return instr
        def immediate(self, instr):
            return re.sub(r"\$[\-]?[0-9]+", 'IMM', instr)
        def address(self, instr):
            return re.sub(r"[^\(\s]*\(.+\)", "ADDR", instr)
        def function(self, instr):
            instr = re.sub(r"callq\s.+", "callq FUNC", instr)
            return re.sub(r"^jmp[\s]+[\w]+", "jmp FUNC", instr)
        def bb_label(self, instr):
            return re.sub(r"\s\..+$", " BB", instr)
        def reg_class(self, instr):
            regs = [r"%[re]?[abcd]x\b",
                    r"%[abcd][lh]\b",
                    r"%[re]?[sd]i\b",
                    r"%[sd]il\b",
                    r"%[x]?mm[0-9]+\b",
                    r"%r[0-9]+[dwb]?\b"]
            reg_pointer = r"%(rbp|rsp|ebp|esp|bp|sp)[lh]?\b"
            for r in regs:
                instr = re.sub(r, "REG", instr)
            return re.sub(reg_pointer, "REGPTR", instr)
        def variable(self, instr):
            instr = re.sub(r"\$[\.a-zA-Z][^\s]+", "VAR", instr)
            il = instr.split()
            for idx, part in enumerate(il):
                if idx == 0:
                    # self.opcode.add(part)
                    continue
                if part not in ["VAR", "IMM", "ADDR", "FUNC", "BB", "REG", "REGPTR"]:
                    self.notrecognized.add(il[idx])
                    il[idx] = "VAR"
            return " ".join(il)
        def classify(self, instr):
            il = instr.split()
            for idx, part in enumerate(il):
                if part not in ["VAR", "IMM", "ADDR", "FUNC", "BB", "REG", "REGPTR"]:
                    matched = False
                    for template, t in self.opcode_classify.items():
                        if re.match(template, part):
                            matched = True
                            il[idx] = t
                            self.code_counter[t] += 1
                            self.opcode_matched.add(part)
                    if not matched:
                        il[idx] = "VAR"
                        self.opcode.add(part)
            return " ".join(il)
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
            # instr = re.sub(reg_pointer, "REGPTR", instr)
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
