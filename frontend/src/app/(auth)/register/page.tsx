import { RegisterForm } from "@/features/auth/components/register-form";
import { PublicRoute } from "@/features/auth/components/public-route";

export default function RegisterPage() {
  return (
    <PublicRoute>
      <main className="flex min-h-svh items-center justify-center p-6">
        <RegisterForm />
      </main>
    </PublicRoute>
  );
}
