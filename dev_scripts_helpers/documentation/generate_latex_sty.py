#!/usr/bin/env python

"""
One off-script to generate a Latex file with abbreviations.

Import as:

import documentation_devto.scripts.generate_latex_sty as ddsglast
"""

# To fix:
# \bb
# \XX
# \vv{\mu}
# \vv{E} = \vv{e}

import pprint
import re
import string
from typing import Dict


def _get_old_map() -> Dict[str, str]:
    r"""
    {'\\aaa': '\\vv{a}',
     '\\aalpha': '\\vv{\\alpha}',
     '\\bb': '\\vv{b}',
     '\\bbeta': '\\vv{\\beta}',
     '\\cc': '\\vv{c}',
     '\\dd': '\\vv{d}',
     '\\ddelta': '\\vv{\\delta}',

     '\\AAA': '\\mat{A}',
     '\\BB': '\\mat{B}',
     '\\CC': '\\mat{C}',
     '\\FF': '\\mat{F}',
     '\\II': '\\mat{I}',
    """
    data = ""

    if False:
        data += r"""
\newcommand{\aaa}{\vv{a}}
\newcommand{\aalpha}{\vv{\alpha}}
\newcommand{\bb}{\vv{b}}
\newcommand{\bbeta}{\vv{\beta}}
\newcommand{\ggamma}{\vv{\gamma}}
\newcommand{\cc}{\vv{c}}
\newcommand{\dd}{\vv{d}}
\newcommand{\ddelta}{\vv{\delta}}
\newcommand{\eee}{\vv{e}}
\newcommand{\ff}{\vv{f}}
\newcommand{\hh}{\vv{h}}
\newcommand{\mmu}{\vv{\mu}}
\newcommand{\oomega}{\vv{\omega}}
\newcommand{\pp}{\vv{p}}
\newcommand{\qq}{\vv{q}}
\newcommand{\rr}{\vv{r}}
\newcommand{\ssigma}{\vv{\sigma}}
\newcommand{\sss}{\vv{s}}
\newcommand{\ttheta}{\vv{\theta}}
\newcommand{\uu}{\vv{u}}
\newcommand{\vvv}{\vv{v}}
\newcommand{\vvarepsilon}{\vv{\varepsilon}}
\newcommand{\vvA}{\vv{A}}
\newcommand{\vvB}{\vv{B}}
\newcommand{\vvF}{\vv{F}}
\newcommand{\vvP}{\vv{P}}
\newcommand{\vvU}{\vv{U}}
\newcommand{\vvX}{\vv{X}}
\newcommand{\vvY}{\vv{Y}}
\newcommand{\ww}{\vv{w}}
\newcommand{\xx}{\vv{x}}
\newcommand{\yy}{\vv{y}}
\newcommand{\zz}{\vv{z}}
"""

    data += r"""
\newcommand{\AAA}{\mat{A}}
\newcommand{\BB}{\mat{B}}
\newcommand{\CC}{\mat{C}}
\newcommand{\II}{\mat{I}}
\newcommand{\FF}{\mat{F}}
\newcommand{\LL}{\mat{L}}
\newcommand{\MM}{\mat{M}}
\newcommand{\NN}{\mat{N}}
\newcommand{\PP}{\mat{P}}
\newcommand{\QQ}{\mat{Q}}
\newcommand{\RR}{\mat{R}}
\newcommand{\SSS}{\mat{S}}
\newcommand{\SSigma}{\mat{\Sigma}}
\newcommand{\UU}{\mat{U}}
\newcommand{\VVV}{\mat{V}}
\newcommand{\XX}{\mat{X}}
\newcommand{\ZZ}{\mat{Z}}
\newcommand{\WW}{\mat{W}}
"""
    old_map_ = {}
    for l_ in data.split("\n"):
        if l_.rstrip().lstrip() == "":
            continue
        m = re.match(r"\\newcommand{(\S+)}{(\S+)}", l_)
        assert m, f"line={l_}"
        # \vvarepsilon \varepsilon
        # print(f"{m.group(1)} -> {m.group(2)}")
        old_map_[m.group(1)] = m.group(2)
    return old_map_


def _get_new_map() -> Dict[str, str]:
    r"""
    Build a map from new abbreviations to the macro
        '\vvv' -> '\vv{v}'
        '\va' -> '\vv{a}'
        '\valpha' -> '\vv{\alpha}'

    {'\\vA': '\\vv{A}',
     '\\vB': '\\vv{B}',
     '\\vC': '\\vv{C}',
     '\\vD': '\\vv{D}',
     '\\vDelta': '\\vv{\\Delta}',
     '\\vE': '\\vv{E}',

     '\\mA': '\\mat{A}',
     '\\mB': '\\mat{B}',
     '\\mC': '\\mat{C}',
     '\\mD': '\\mat{D}',
     '\\mDelta': '\\mat{\\Delta}',
    """
    new_map_ = {}
    # Vector.
    if True:
        all_letters = list(string.ascii_letters)

        if True:
            all_letters.extend(
                r"""
            \alpha
            \beta
            \gamma \Gamma
            \delta \Delta
            \epsilon \varepsilon
            \zeta
            \eta
            \theta \vartheta
            \iota
            \kappa
            \lambda \Lambda
            \mu
            \nu
            \xi \Xi
            \pi \Pi
            \rho \varrho
            \sigma \Sigma
            \tau
            \upsilon \Upsilon
            \phi \varphi \Phi
            \chi
            \psi \Psi
            \omega \Omega""".split()
            )

        for line in all_letters:
            if line == "v":
                # \newcommand{\vvv}{\vv{v}}
                new_map_[r"\vvv"] = r"\vv{v}"
            elif line.startswith("\\"):
                # \newcommand{\valpha}{\vv{\alpha}}
                new_map_[rf"\v{line[1:]}"] = rf"\vv{{{line}}}"
            else:
                # \newcommand{\va}{\vv{a}}
                new_map_[rf"\v{line}"] = rf"\vv{{{line}}}"

    # Matrix.
    if True:
        all_letters = list(string.ascii_uppercase)

        if True:
            all_letters.extend(
                r"""
            \Gamma
            \Delta
            \Lambda
            \Xi
            \Pi
            \Sigma
            \Upsilon
            \Psi
            \Omega""".split()
            )

        for l_ in all_letters:
            if l_.startswith("\\"):
                # \newcommand{\valpha}{\vv{\alpha}}
                new_map_[rf"\m{l_[1:]}"] = rf"\mat{{{l_}}}"
            else:
                # \newcommand{\va}{\vv{a}}
                new_map_[rf"\m{l_}"] = rf"\mat{{{l_}}}"
    return new_map_


def generate_latex() -> None:
    txt = []
    #
    map_ = _get_new_map()
    for k in sorted(map_.keys()):
        v = map_[k]
        cmd = rf"\newcommand{{{k}}}{{{v}}}"
        txt.append(cmd)
    #
    txt = "\n".join(txt)
    file_name = "./latex_abbrevs.tmp.sty"
    with open(file_name, mode="w") as f:
        f.write(txt)
    #
    print(txt)


def generate_vim_spell_check() -> None:
    print("# vim spell check.")
    txt = []
    new_map_ = _get_new_map()
    for k, _ in sorted(new_map_.items()):
        arg1 = k.replace("\\", "")
        txt.append(arg1)
    #
    txt = "\n".join(txt)
    file_name = "./vimspell.txt"
    with open(file_name, mode="w") as f:
        f.write(txt)
    #
    print(txt)


# /////////////////////////////////////////////////////////////////////////////


def generate_mathcal() -> None:
    txt1 = []
    txt2 = []
    #
    for k in string.ascii_letters:
        # \def\calA{\mathcal{D}}
        cmd = rf"\newcommand{{\cal{k}}}{{\mathcal{{{k}}}}}"
        txt1.append(cmd)
        txt2.append(f"cal{k}")
    #
    print("\n".join(txt1))
    print("\n".join(txt2))


# /////////////////////////////////////////////////////////////////////////////


# TODO(gp): This is probably not needed anymore.
def generate_perl1() -> None:
    r"""
    Convert long form to old abbreviations.

    perl -i -pe 's/\\vv\{A\}/\\vvA/g' $filename
    perl -i -pe 's/\\vv\{B\}/\\vvB/g' $filename
    perl -i -pe 's/\\vv\{X\}/\\vvX/g' $filename
    """
    print("# Convert long form to old abbreviations.")
    old_map_ = _get_old_map()
    for k, v in sorted(old_map_.items()):
        cmd = rf"""perl -i -pe 's/{v}/{k}/g' $filename"""
        print(cmd)


def generate_perl2() -> None:
    r"""
    Convert long form to new abbreviations.

    perl -i -pe 's/\\vv\{A\}/\\vA/g' $filename
    perl -i -pe 's/\\vv\{B\}/\\vB/g' $filename
    perl -i -pe 's/\\vv\{X\}/\\vX/g' $filename
    """
    print("# Convert long form to new abbreviations.")
    new_map_ = _get_new_map()
    for k, v in sorted(new_map_.items()):
        arg1 = v.replace("\\", "\\\\")
        arg2 = k.replace("\\", "\\\\")
        cmd = rf"""perl -i -pe 's/{arg1}/{arg2}/g' $filename"""
        print(cmd)


def generate_perl3() -> None:
    r"""
    Generate perl from old to new abbreviations.

    perl -i -pe 's/\\aaa/\\va/g' $filename
    perl -i -pe 's/\\aalpha/\\valpha/g' $filename
    perl -i -pe 's/\\bb(?![RCNZ])/\\vb/g' $filename
    """
    print("# Generate perl from old to new abbreviations.")
    new_map_ = _get_new_map()
    rev_new_map = {v: k for k, v in new_map_.items()}
    old_map_ = _get_old_map()
    for k, v in old_map_.items():
        new_macro = rev_new_map[v]
        # perl -i -pe 's/\\bb[^RCNZ]/\\vb/g' $filename
        arg1 = k.replace("\\", "\\\\")
        arg2 = new_macro.replace("\\", "\\\\")
        # To avoid collisions.
        if arg1 == r"\bb":
            arg1 += "(?![RCNZ])"
        elif arg1 in ("uu", "vvv", "xx"):
            arg1 += "(?!hat)"
        cmd = rf"""perl -i -pe 's/{arg1}/{arg2}/g' $filename"""
        print(cmd)


if __name__ == "__main__":
    if False:
        old_map = _get_old_map()
        new_map = _get_new_map()
        print("*" * 80)
        print("old_map")
        print("*" * 80)
        pprint.pprint(old_map)
        #
        print("*" * 80)
        print("new_map")
        print("*" * 80)
        pprint.pprint(new_map)
    # generate_latex()
    # generate_perl1()
    # generate_perl2()
    # generate_perl3()
    # generate_vim_spell_check()
    generate_mathcal()
