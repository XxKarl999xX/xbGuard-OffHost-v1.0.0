import argparse
import os
import subprocess
import sys

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC     = os.path.join(ROOT, "src")
INCLUDE = os.path.join(ROOT, "include")
BUILD   = os.path.join(ROOT, "build")
OBJ     = os.path.join(BUILD, "obj")

NAME       = "xbg"
DEF_FILE   = os.path.join(ROOT, "config", NAME + ".def")
XEX_CONFIG = os.path.join(ROOT, "config", NAME + ".xexcfg")

DEFAULT_XEDK = r"C:\Program Files (x86)\Microsoft Xbox 360 SDK"

LIBS = [
    "xapilib.lib", "xboxkrnl.lib", "libcMT.lib", "libcpMT.lib"
]

CL_FLAGS = [
    "/nologo",
    "/c",
    "/EHa",
    "/GS-",
    "/GR-",
    "/O2",
    "/MT",
    "/W3",
    "/D_XBOX",
    "/DNDEBUG",
    "/I" + INCLUDE,
]

LINK_FLAGS = [
    "/nologo",
    "/DLL",
    "/SUBSYSTEM:XBOX",
    "/MACHINE:PPCBE",
    "/NODEFAULTLIB:libc.lib",
    "/DEF:" + DEF_FILE,
    "/XEX:NO",
]

def find_xedk():
    xedk = os.environ.get("XEDK") or DEFAULT_XEDK

    if not os.path.isdir(os.path.join(xedk, "bin", "win32")):
        sys.exit("Xbox 360 SDK not found at %r.\n" % xedk)

    return xedk


def tool_env(xedk):
    env            = dict(os.environ)
    env["XEDK"]    = xedk
    env["INCLUDE"] = os.path.join(xedk, "include", "xbox")
    env["LIB"]     = os.path.join(xedk, "lib", "xbox")
    env["PATH"]    = os.path.join(xedk, "bin", "win32") + os.pathsep + env.get("PATH", "")

    return env


def run(cmd, env):
    proc = subprocess.Popen(
        cmd, env = env, cwd = ROOT, stdout = subprocess.PIPE, stderr = subprocess.STDOUT
    )
    out = proc.communicate()[0].decode("utf-8", "replace")

    if out.strip():
        sys.stdout.write(out if out.endswith("\n") else out + "\n")

    return proc.returncode


def sources():
    found = []

    for base, _dirs, files in os.walk(SRC):
        for f in files:
            if f.endswith(".cpp"):
                found.append(os.path.join(base, f))

    return sorted(found)


def obj_for(path):
    rel = os.path.relpath(path, SRC)

    return os.path.join(OBJ, rel.replace(os.sep, "_")[:- len(".cpp")] + ".obj")


def needs_rebuild(src, obj):
    if not os.path.exists(obj):
        return True

    return os.path.getmtime(src) > os.path.getmtime(obj)


def compile_all(xedk, env, force):
    cl     = os.path.join(xedk, "bin", "win32", "cl.exe")
    objs   = []
    failed = []

    for src in sources():
        obj = obj_for(src)

        objs.append(obj)
        if not force and not needs_rebuild(src, obj):
            continue
        print("cl   %s" % os.path.relpath(src, ROOT))

        if run([cl] + CL_FLAGS + ["/Fo" + obj, src], env) != 0:
            failed.append(os.path.relpath(src, ROOT))

    if failed:
        sys.exit("compile failed: %s" % ", ".join(failed))

    return objs


def link(xedk, env, objs):
    linker = os.path.join(xedk, "bin", "win32", "link.exe")
    dll    = os.path.join(BUILD, NAME + ".dll")

    print("link %s" % os.path.relpath(dll, ROOT))
    cmd = (
        [linker]
        + LINK_FLAGS
        + [
        "/OUT:" + dll,
        "/IMPLIB:" + os.path.join(BUILD, NAME + ".lib"),
    ]
        + objs
        + LIBS
    )

    if run(cmd, env) != 0:
        sys.exit("link failed")

    return dll


def make_xex(xedk, env, dll):
    imagexex = os.path.join(xedk, "bin", "win32", "imagexex.exe")
    xex      = os.path.join(BUILD, NAME + ".xex")

    print("xex  %s" % os.path.relpath(xex, ROOT))
    cmd = [imagexex, "/nologo", "/IN:" + dll, "/OUT:" + xex, "/CONFIG:" + XEX_CONFIG]

    if run(cmd, env) != 0:
        sys.exit("imagexex failed")

    return xex


def deploy(xedk, env, xex, console, remote_dir):
    if not console:
        print(
            "deploy skipped: no console set "
            "(use --console NAME or the XBOX_CONSOLE environment variable)"
        )

        return

    xbcp = os.path.join(xedk, "bin", "win32", "xbcp.exe")
    dest = "xe:\\%s\\%s" % (console, remote_dir.strip("\\"))

    print("copy %s -> %s" % (os.path.basename(xex), dest))

    if run([xbcp, "/y", xex, dest + "\\"], env) != 0:
        sys.exit("deploy failed")


def main():
    parser = argparse.ArgumentParser(description = "Build xbg.xex")

    parser.add_argument("--build-only", action = "store_true", help = "skip deployment")
    parser.add_argument("--rebuild", action = "store_true", help = "ignore timestamps")
    parser.add_argument("--console", default = os.environ.get("XBOX_CONSOLE"))
    args = parser.parse_args()
    xedk = find_xedk()
    env  = tool_env(xedk)

    if not os.path.isdir(OBJ):
        os.makedirs(OBJ)

    objs = compile_all(xedk, env, args.rebuild)
    dll  = link(xedk, env, objs)
    xex  = make_xex(xedk, env, dll)

    print("built %s (%d bytes)" % (os.path.relpath(xex, ROOT), os.path.getsize(xex)))

    if not args.build_only:
        deploy(xedk, env, xex, args.console, args.remote_dir)

if __name__ == "__main__":
    main()
