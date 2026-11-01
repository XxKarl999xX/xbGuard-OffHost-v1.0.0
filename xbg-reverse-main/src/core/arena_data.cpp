// Placeholder: no data-region dump has been supplied.
//
// Run `python scripts/gen_arena.py <dump.bin>` with a dump of the original
// 0x90B00000..0x90C10000 region to replace this file with the real contents.
// With this placeholder the image still links and boots, but the arena is all
// zeroes, so anything the menu reads back through xbg::At() reads as zero.
//
// The definitions are spelled `extern const` because a namespace-scope const
// otherwise has internal linkage in C++ and arena.cpp could not see it.

extern "C" {
    extern const unsigned int g_xbgDumpSize       = 0;
    extern const unsigned int g_xbgDumpChunkSize  = 0;
    extern const unsigned int g_xbgDumpChunkCount = 0;
    extern const char* const g_xbgDumpChunks[]    = { 0 };
}
