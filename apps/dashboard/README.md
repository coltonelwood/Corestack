# @abf/dashboard

The web dashboard for Autonomous Business Factory. Built with Next.js 14 (App Router), TypeScript, Tailwind CSS, and shadcn/ui.

## Development

```bash
# From the monorepo root
pnpm dev

# Or directly
cd apps/dashboard && pnpm dev
```

Runs on [http://localhost:3000](http://localhost:3000).

## Environment Variables

Copy `.env.example` to `.env.local` and fill in your Supabase credentials.

## Structure

```
src/
  app/
    layout.tsx    → Root layout with global styles
    page.tsx      → Home page
    globals.css   → Tailwind imports and global styles
```
