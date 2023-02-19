class Path():
    def __init__(self):
        self.x0 = None
        self.y0 = None
        self.z0 = None
        self.x1 = None
        self.y1 = None
        self.z1 = None

    def add_x0(self, x0):
        self.x0 = x0
    def add_y0(self, y0):
        self.y0 = y0
    def add_z0(self, z0):
        self.z0 = z0
    def add_x1(self, x1):
        self.x1 = x1
    def add_y1(self, y1):
        self.y1 = y1
    def add_z1(self, z1):
        self.z1 = z1

    def get_vals(self):
        return (self.x0, self.y0, self.z0, self.x1, self.y1, self.z1)
    def check_vals(self):
        return self.x0 is not None and self.y0 is not None and self.z0 is not None and self.x1 is not None and self.y1 is not None and self.z1 is not None 

def parse_dxf(dxf_path):
    with open(dxf_path, 'r') as f:
        f_lines = f.readlines()

    path = None
    paths = []
    while f_lines:
        line = f_lines[0]
        if line.strip() == 'LINE':
            if path and path.check_vals:
                print(path.get_vals())
                paths.append(path)
            path = Path()

        if path and line.strip() == '10' and len(f_lines)>=2:
            path.add_x0(float(f_lines[1].strip()))
            f_lines.pop(1)

        if path and line.strip() == '11' and len(f_lines)>=2:
            print(f_lines[0], f_lines[1])
            path.add_y0(float(f_lines[1].strip()))
            f_lines.pop(1)

        if path and line.strip() == '20' and len(f_lines)>=2:
            path.add_x1(float(f_lines[1].strip()))
            f_lines.pop(1)

        if path and line.strip() == '21' and len(f_lines)>=2:
            path.add_y1(float(f_lines[1].strip()))
            f_lines.pop(1)

        if path and line.strip() == '30' and len(f_lines)>=2:
            path.add_z0(float(f_lines[1].strip()))
            f_lines.pop(1)

        if path and line.strip() == '31' and len(f_lines)>=2:
            path.add_z1(float(f_lines[1].strip()))
            f_lines.pop(1)

        f_lines.pop(0)

    return paths


def show_dxf(paths):

    ax = plt.axes(projection='3d')

    for path in paths:
        print(path.get_vals())
        print(f'{path.x0} | {path.y0} | {path.z0} xyz -> {path.x1} | {path.y1} | {path.z1}xyz')
        plt.plot([path.x0,path.x1],[path.y0,path.y1], [path.z0, path.z1])

    plt.show()


if __name__ == '__main__':
    paths = parse_dxf('dxf/cube.dxf')
    show_dxf(paths)
