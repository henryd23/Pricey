import React, { useState } from 'react';
import { X, Lock, Mail, User as UserIcon, LogIn, UserPlus } from 'lucide-react';
import { loginUser, registerUser } from '../api';

export default function AuthModal({ onClose, onSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      let data;
      if (isRegister) {
        data = await registerUser(email, password, fullName);
      } else {
        data = await loginUser(email, password);
      }
      onSuccess(data.user);
      onClose();
    } catch (err) {
      setError(err.message || 'Si è verificato un errore.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card auth-modal-card">
        <div className="modal-header">
          <div className="modal-title-group">
            {isRegister ? (
              <UserPlus className="modal-icon text-blue" size={22} />
            ) : (
              <LogIn className="modal-icon text-blue" size={22} />
            )}
            <h3>{isRegister ? 'Crea il tuo Account' : 'Accedi a Pricey'}</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div className="alert-box error">{error}</div>}

            {isRegister && (
              <div className="form-field">
                <label className="input-label">Nome Completo (opzionale):</label>
                <div className="input-with-icon">
                  <UserIcon className="field-icon" size={18} />
                  <input
                    type="text"
                    placeholder="Mario Rossi"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                </div>
              </div>
            )}

            <div className="form-field">
              <label className="input-label">Email:</label>
              <div className="input-with-icon">
                <Mail className="field-icon" size={18} />
                <input
                  type="email"
                  placeholder="nome@esempio.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div className="form-field">
              <label className="input-label">Password:</label>
              <div className="input-with-icon">
                <Lock className="field-icon" size={18} />
                <input
                  type="password"
                  placeholder="Minimo 6 caratteri"
                  required
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            <div className="auth-toggle-row">
              {isRegister ? (
                <p>
                  Hai già un account?{' '}
                  <button
                    type="button"
                    className="btn-text-link"
                    onClick={() => {
                      setIsRegister(false);
                      setError(null);
                    }}
                  >
                    Accedi
                  </button>
                </p>
              ) : (
                <p>
                  Non hai ancora un account?{' '}
                  <button
                    type="button"
                    className="btn-text-link"
                    onClick={() => {
                      setIsRegister(true);
                      setError(null);
                    }}
                  >
                    Registrati gratis
                  </button>
                </p>
              )}
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={submitting}>
              Annulla
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Attendere...' : isRegister ? 'Registrati' : 'Accedi'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
