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

cwd = os.path.dirname(os.path.realpath(__file__))
os.chdir(cwd)

ret = subprocess.call(
    f'./build-bleeding-edge-toolchain.sh {"--resume" if not args.noResume else ""} --keep-build-folders --skip-documentation {"--enable-win" if args.platform == "mingw32" else ""}{"32" if args.arch == "i686" else "64"}',
    shell=True,
)
if ret != 0:
    # Ok, sources weren't copied right, do it again.
    ret = subprocess.call(
        f'./build-bleeding-edge-toolchain.sh {"--resume" if not args.noResume else ""} --keep-build-folders --skip-documentation {"--enable-win" if args.platform == "mingw32" else ""}{"32" if args.arch == "i686" else "64"}',
        shell=True,
    )
assert ret == 0, f"Subcommand failed with exit code {ret}."

buildArtifacts = f'{cwd}/install{"Native" if args.platform == "linux" else "Win32" if args.arch == "i686" else "Win64"}'

ret = subprocess.call(
    f"7z a arm-none-eabi-gcc.7z {buildArtifacts}",
    shell=True,
)
assert ret == 0, f"Subcommand failed with exit code {ret}."

ret = subprocess.call(
    f'7z rn arm-none-eabi-gcc.7z install{"Native" if args.platform == "linux" else "Win32" if args.arch == "i686" else "Win64"}/ arm-none-eabi-gcc/',
    shell=True,
)
assert ret == 0, f"Subcommand failed with exit code {ret}."
