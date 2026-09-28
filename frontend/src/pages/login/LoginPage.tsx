import { useState, type FormEvent, type ReactElement } from 'react';
import { useLocation, useNavigate, type Location } from 'react-router-dom';
import { ArrowRight, Lock, User } from 'lucide-react';
import { Alert } from '../../components/ui/Alert';
import { Button } from '../../components/ui/Button';
import { TextField } from '../../components/ui/TextField';
import { useAuth } from '../../hooks/useAuth';
import { describeError } from '../../utils/errorMessages';
import { LoginHighlights } from './LoginHighlights';
import styles from './LoginPage.module.css';

interface LoginLocationState {
  from?: Location;
}

export function LoginPage(): ReactElement {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setErrorMessage(null);
    setSubmitting(true);
    try {
      await signIn(username.trim(), password);
      const from = (location.state as LoginLocationState | null)?.from?.pathname;
      navigate(from && from !== '/login' ? from : '/dashboard', { replace: true });
    } catch (error) {
      setErrorMessage(describeError(error, 'Não foi possível entrar. Tente novamente.'));
      setPassword('');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className={styles.page}>
      <main className={styles.card}>
        <section className={styles.formColumn}>
          <p className={styles.product}>Sistema de Gestão Clínica Ambulatorial</p>
          <h1 className={styles.title}>Bem-vindo de volta!</h1>
          <p className={styles.subtitle}>Acesse o sistema com sua conta individual.</p>
          <form className={styles.form} onSubmit={handleSubmit} noValidate>
            {errorMessage && <Alert tone="error">{errorMessage}</Alert>}
            <TextField
              label="Usuário"
              name="username"
              autoComplete="username"
              placeholder="Digite seu usuário"
              icon={<User size={18} />}
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
              autoFocus
            />
            <TextField
              label="Senha"
              name="password"
              type="password"
              autoComplete="current-password"
              placeholder="Digite sua senha"
              icon={<Lock size={18} />}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
            <Button
              type="submit"
              size="lg"
              fullWidth
              isLoading={isSubmitting}
              disabled={!username.trim() || !password}
              icon={<ArrowRight size={18} />}
            >
              {isSubmitting ? 'Entrando…' : 'Entrar'}
            </Button>
          </form>
          <p className={styles.help}>Esqueceu a senha? Procure a gestão da clínica.</p>
        </section>
        <LoginHighlights />
      </main>
    </div>
  );
}
