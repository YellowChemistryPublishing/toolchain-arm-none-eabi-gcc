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
    "--no-resume",
    action="store_true",
    default=False,
    dest="noResume",
)
args = parser.parse_args()
if (args.platform == "linux"):
    args.arch = "x86_64"

cwd = os.path.dirname(os.path.realpath(__file__))
os.chdir(cwd)

ret = subprocess.call(
    (
        f'./build-bleeding-edge-toolchain.sh {"--resume" if not args.noResume else ""} --keep-build-folders --skip-documentation '
        f'{"--enable-win32" if args.platform == "mingw32" and args.arch == "i686" else "--enable-win64" if args.platform == "mingw32" and args.arch == "x86_64" else ""}'
    ),
    shell=True,
)
if ret != 0:
    # Ok, sources weren't copied right, do it again.
    ret = subprocess.call(
        (
            f'./build-bleeding-edge-toolchain.sh {"--resume" if not args.noResume else ""} --keep-build-folders --skip-documentation '
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
