#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt

label_pr = {
    'misa_data_arm': {
        64: (0.999765175531, 0.173718785703),
        32: (0.970466241647, 0.25776277134),
        16: (0.829255850532, 0.397972090746),
        8: (0.481826869876, 0.488575159132),
        4: (0.26125713431, 0.57013016158),
        2: (0.116458092788, 0.714042353517)
    },
    'misa_data_arm_sublabel_64': {
        64: (0.999765175531, 0.173718785703),
        32: (0.991094559585, 0.187316386486),
        16: (0.955586041327, 0.22737473478),
        8: (0.607289072466, 0.509925330504),
        4: (0.480991849616, 0.781989554431),
        2: (0.105770704073, 0.999908193243)
    },
    'misa_data_arm_sublabel_32': {
        1: (0.0512282135603, 1.0),
        2: (0.117581419865, 0.992114819651),
        4: (0.24416339336, 0.787528562102),
        8: (0.319770650057, 0.514281051085),
        16: (0.56282517994, 0.345387220499),
        32: (0.970466241647, 0.25776277134)
    },
    'misa_data_arm_sublabel_128': {
        64: (1.0, 0.173963603721),
        32: (0.791864237584, 0.258935857679),
        16: (0.345337137552, 0.675361106577),
        8: (0.0942279757533, 0.998510690387)
    },
    'misa_data_x86': {
        64: (0.999904861574, 0.303275140672),
        32: (0.967022613065, 0.35538883278),
        16: (0.256160303276, 0.491357668446),
        8: (0.153800590761, 0.569441639013),
        4: (0.0351849140209, 0.797374116289)
    },
    'misa_data_x86_sublabel_64': {
        64: (0.999904861574, 0.303275140672),
        32: (0.957914465837, 0.324455345549),
        16: (0.755322285782, 0.369585918338),
        8: (0.663807890223, 0.524859327658),
        4: (0.252757858733, 0.861491848218),
        2: (0.0349623328131, 0.999971144135)
    },
    'misa_data_x86_sublabel_32': {
        32: (0.967022613065, 0.35538883278),
        16: (0.495092518101, 0.443947482326),
        8: (0.369097629135, 0.59073726735),
        4: (0.128544858814, 0.853585341221),
        2: (0.0477360409458, 0.99685471072)
    },
    'misa_data_x86_pca': {
        64: (0.995382150598, 0.30477564565),
        32: (0.959212253829, 0.316231424037),
        16: (0.386629962622, 0.441754436589),
        8: (0.0687265594088, 0.711729909104)
    },
    'misa_data_x86_95': {
        64: (0.999524307868, 0.788501951366),
        32: (0.836212311558, 0.799309516662),
        16: (0.170457622529, 0.850420294206),
        8: (0.0921759190704, 0.887646352447),
        4: (0.0158168494904, 0.932302611828)
    },
    'vs_data': {
        8: (0.3280184346050943, 0.8051474775082564),
        16: (0.7970342910101946, 0.7835098508142581),
        32: (0.998617010767559, 0.767490414910982),
        64: (1.0, 0.7626693998405648)
    },
    'vs_data_95': {
        64: (1.0, 0.93891952518927),
        32: (0.9965919193914847, 0.9429385923918123),
        16: (0.782051282051282, 0.9464435928591457),
        8: (0.31607924405746896, 0.9551359940181325)
    }
}


def print_f1():
    for name, data in label_pr.items():
        so = sorted(data.items(), key=lambda x:x[0])
        label, pts = zip(*so)
        print(name)
        for i in range(len(pts)):
            x, y = pts[i]
            f1 = 2 * x * y / (x + y)
            print(str(label[i]) + "\t" + str(f1))
        print("=================================")


def make_plot(lines, format_line, figname):
    for idx, cur_label in enumerate(lines):
        data_sorted = sorted(label_pr[cur_label].items(), key=lambda x: x[0], reverse=True)
        label, pts = zip(*data_sorted)
        xs, ys = zip(*pts)

        plt.plot(ys, xs, format_line[idx], label=cur_label)

        for i in range(len(pts)):
            plt.annotate(label[i], (pts[i][1], pts[i][0]),
                         textcoords="offset points",
                         xytext=(0,10),
                         ha='center')
    plt.ylabel("precision")
    plt.xlabel("recall")
    plt.legend()
    plt.savefig(figname)


def main():
    parser = argparse.ArgumentParser(description="""Tinh f1 hoac ve plot cho LSH label""")
    parser.add_argument('--f1', action='store_true', help='In bang F1')
    parser.add_argument('--line', choices=list(label_pr.keys()), action='append', help='Ve plot')
    parser.add_argument('--save_fig', default='lsh_plot.png', help='Ten figure')

    args = parser.parse_args()
    if args.f1:
        print_f1()
    if args.line:
        if len(args.line) > 3:
            print("Only have format for three lines at a time")
            exit()
        format_line = ['bx-', 'ro-', 'gv-']
        make_plot(args.line, format_line, args.save_fig)


if __name__=='__main__':
    main()
