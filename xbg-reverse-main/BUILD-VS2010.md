# XBGuard: Visual Studio 2010

Open **XBGuard.sln** from this directory in Visual Studio 2010. Select
**Release | Xbox 360**, then choose **Build > Build Solution** (F7).
The output is **build\Release\xbg.xex**. Debug builds use
**build\Debug\xbg.xex**.

This is a native VS 2010 Xbox 360 C++ project, using the Xbox 360 SDK's
PowerPC compiler, linker and ImageXex tool. It requires the Xbox 360 SDK
with VS 2010 integration, already installed on this PC. No VS 2022 toolchain,
Python build wrapper or Makefile project is involved.

The project includes all 24 C++ source files, the headers and the existing
export definition and XEX configuration. Source folders also appear as
Solution Explorer filters. Intermediate files retain their source directory
structure so repeated filenames such as input.cpp and state.cpp cannot
overwrite each other's object files. Debug and Release outputs are separate.

The DLL link setting uses the CRT's DLL startup path and the existing DllMain.
XEX packaging uses config\xbg.xexcfg. Its base address was changed from
0x91E00000 to 0x81E00000 because this SDK's ImageXex rejects the original
address (IM1038); the latter is accepted for the configured system DLL.
The linker uses the same address. Console loading, address availability and
gameplay still require testing on the intended console/game build.

Building does not deploy to a console. No console connection is needed to
build the XEX. Existing source warnings about pointer sign extension remain;
a successful build does not establish runtime correctness of the reversed
menu.

Generated binaries, debug symbols, build logs and local Visual Studio caches
were removed for source sharing. Rebuilding recreates them. These files can
embed the builder's username, absolute paths and device settings, including
inside DLL/XEX debug records. The ignore rules exclude them from version
control; when sharing an archive, exclude build/, ipch/, .vs/, *.suo, *.sdf,
*.vcxproj.user and *.log as well. Keep the solution, project and filters.

The commands below save local build logs (do not include them in a shared copy):

```bat
"C:\Program Files (x86)\Microsoft Visual Studio 10.0\Common7\IDE\devenv.com" XBGuard.sln /Rebuild "Release|Xbox 360" /Out vs2010-release-build.log
"C:\Program Files (x86)\Microsoft Visual Studio 10.0\Common7\IDE\devenv.com" XBGuard.sln /Rebuild "Debug|Xbox 360" /Out vs2010-debug-build.log
```
