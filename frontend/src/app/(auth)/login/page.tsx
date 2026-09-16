import { LoginForm } from "@/features/auth/components/login-form";
import { PublicRoute } from "@/features/auth/components/public-route";

export default function LoginPage() {
  return (
    <PublicRoute>
      <main className="flex min-h-svh items-center justify-center p-6">
        <LoginForm />
      </main>
    </PublicRoute>
  );
}
