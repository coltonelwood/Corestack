"use client";

import { useState } from "react";
import { Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { signIn, signUp } from "@/app/actions/auth";
import { Loader2 } from "lucide-react";

export default function LoginPage() {
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [mode, setMode] = useState<"login" | "signup">("login");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setError(null);
    setMessage(null);

    const formData = new FormData(e.currentTarget);

    if (mode === "signup") {
      const result = await signUp(formData);
      setPending(false);
      if (result?.error) {
        setError(result.error);
      } else if (result?.message) {
        setMessage(result.message);
      }
    } else {
      const result = await signIn(formData);
      setPending(false);
      if (result?.error) {
        setError(result.error);
      }
    }
  }

  return (
    <div className="flex min-h-screen">
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-primary p-12 text-primary-foreground">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20">
            <Zap className="h-5 w-5" />
          </div>
          <span className="text-xl font-bold">Autonomous Business Factory</span>
        </div>
        <div>
          <h1 className="text-4xl font-bold leading-tight">
            Run businesses
            <br />
            on autopilot.
          </h1>
          <p className="mt-4 text-lg text-primary-foreground/80 max-w-md">
            AI agents that research markets, create products, launch campaigns,
            and optimize operations — all autonomously.
          </p>
        </div>
        <p className="text-sm text-primary-foreground/60">
          &copy; 2025 Autonomous Business Factory
        </p>
      </div>

      <div className="flex w-full lg:w-1/2 items-center justify-center p-8">
        <div className="w-full max-w-sm space-y-8">
          <div className="lg:hidden flex items-center gap-2 justify-center mb-4">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
              <Zap className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="text-lg font-bold">ABF</span>
          </div>

          <div className="text-center lg:text-left">
            <h2 className="text-2xl font-bold tracking-tight">
              {mode === "login" ? "Welcome back" : "Create your account"}
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {mode === "login"
                ? "Sign in to your account to continue"
                : "Get started with Autonomous Business Factory"}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium leading-none">Email</label>
              <Input id="email" name="email" type="email" placeholder="you@example.com" required />
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium leading-none">Password</label>
              <Input id="password" name="password" type="password" placeholder="Enter your password" required minLength={6} />
            </div>

            {error && (
              <p className="text-sm text-destructive bg-destructive/10 rounded-md px-3 py-2">{error}</p>
            )}
            {message && (
              <p className="text-sm text-emerald-600 bg-emerald-50 rounded-md px-3 py-2">{message}</p>
            )}

            <Button type="submit" className="w-full" disabled={pending}>
              {pending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {mode === "login" ? "Sign in" : "Create account"}
            </Button>
          </form>

          <p className="text-center text-sm text-muted-foreground">
            {mode === "login" ? (
              <>
                Don&apos;t have an account?{" "}
                <button className="text-primary font-medium hover:underline" onClick={() => { setMode("signup"); setError(null); setMessage(null); }}>
                  Get started
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button className="text-primary font-medium hover:underline" onClick={() => { setMode("login"); setError(null); setMessage(null); }}>
                  Sign in
                </button>
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
