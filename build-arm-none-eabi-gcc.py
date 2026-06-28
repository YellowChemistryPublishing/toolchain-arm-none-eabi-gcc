import argparse
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument(
    "--host-arch",
    action="store",
    default="i686",
    dest="arch",
    choices=["x86_64", "i686"],
)
parser.add_argument(
    "--host-platform",
    action="store",
    default="mingw32",
    dest="platform",
    choices=["linux", "mingw32"],
)
parser.add_argument(
    "--resume",
    action="store_true",
    default=False,
    dest="resume",
)
args = parser.parse_args()
if args.platform == "linux":
    args.arch = "x86_64"

cwd = os.path.dirname(os.path.realpath(__file__))
os.chdir(cwd)

ret = subprocess.call("sudo apt-get update", shell=True)
assert ret == 0, f"Subcommand failed with exit code {ret}."

ret = subprocess.call(
    "sudo apt install -y "
    + " ".join(
        [
            "autoconf",
            "autogen",
            "automake",
            "binutils",
            "bison",
            "build-essential",
            "coreutils",
            "curl",
            "flex",
            "g++",
            "gawk",
            "gcc",
            "gdb",
            "git-core",
            "less",
            "libbz2-dev",
            "libc-dev",
            "libc6-dev",
            "libelf-dev",
            "libglib2.0-dev",
            "libgmp-dev",
            "libisl-dev",
            "libltdl-dev",
            "libmpc-dev",
            "libmpfr-dev",
            "libncurses5-dev",
            "libreadline-dev",
            "libtool",
            "linux-libc-dev",
            "m4",
            "make",
            "perl",
            "pkg-config",
            "python3",
            "rsync",
            "shtool",
            "time",
            "wget",
            "zlib1g-dev",
            "p7zip-full",
            *(
                ["gcc-mingw-w64-base", "mingw-w64-common"]
                if args.platform == "mingw32"
                else []
            ),
            *(
                [
                    "binutils-mingw-w64-i686",
                    "g++-mingw-w64-i686-posix",
                    "gcc-mingw-w64-i686-posix",
                    "mingw-w64-i686-dev",
                ]
                if args.platform == "mingw32" and args.arch == "i686"
                else (
                    [
                        "binutils-mingw-w64-x86-64",
                        "g++-mingw-w64-x86-64-posix",
                        "gcc-mingw-w64-x86-64-posix",
                        "mingw-w64-x86-64-dev",
                    ]
                    if args.platform == "mingw32" and args.arch == "x86_64"
                    else []
                )
            ),
        ]
    ),
    shell=True,
    env={"DEBIAN_FRONTEND": "noninteractive", **os.environ},
)
assert ret == 0, f"Subcommand failed with exit code {ret}."

if args.platform == "mingw32":
    triplet = f"{args.arch}-w64-mingw32"
    for tool in ("gcc", "g++"):
        ret = subprocess.call(
            f"sudo update-alternatives --set {triplet}-{tool} /usr/bin/{triplet}-{tool}-posix",
            shell=True,
        )
        assert ret == 0, f"Subcommand failed with exit code {ret}."

ret = subprocess.call(
    (
        f'./build-bleeding-edge-toolchain.sh {"--resume" if args.resume else ""} --keep-build-folders --skip-documentation '
        f'{"--enable-win32" if args.platform == "mingw32" and args.arch == "i686" else "--enable-win64" if args.platform == "mingw32" and args.arch == "x86_64" else ""}'
    ),
    shell=True,
)
for _ in range(4):
    # Try harder.
    if ret != 0:
        # Ok, sources weren't copied right, do it again, from scratch.
        ret = subprocess.call(
            (
                f"./build-bleeding-edge-toolchain.sh {"--resume" if args.resume else ""} --keep-build-folders --skip-documentation "
                f'{"--enable-win32" if args.platform == "mingw32" and args.arch == "i686" else "--enable-win64" if args.platform == "mingw32" and args.arch == "x86_64" else ""}'
            ),
            shell=True,
        )
assert ret == 0, f"Subcommand failed with exit code {ret}."

buildArtifacts = f'{cwd}/install{"Native" if args.platform == "linux" else "Win32" if args.arch == "i686" else "Win64"}'

ret = subprocess.call(
    f"7z a {args.arch}-{args.platform}-to-arm-none-eabi-gcc.7z {buildArtifacts}",
    shell=True,
)
assert ret == 0, f"Subcommand failed with exit code {ret}."

ret = subprocess.call(
    f'7z rn {args.arch}-{args.platform}-to-arm-none-eabi-gcc.7z install{"Native" if args.platform == "linux" else "Win32" if args.arch == "i686" else "Win64"}/ arm-none-eabi-gcc/',
    shell=True,
)
assert ret == 0, f"Subcommand failed with exit code {ret}."
