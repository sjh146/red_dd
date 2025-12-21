from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading

class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("파일 암호화/복호화 도구")
        self.root.geometry("700x400")
        self.root.resizable(False, False)
        
        # 탭 컨트롤 생성
        self.tab_control = ttk.Notebook(root)
        
        # 암호화 탭
        self.encrypt_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.encrypt_tab, text='암호화')
        self.setup_encrypt_tab()
        
        # 복호화 탭
        self.decrypt_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.decrypt_tab, text='복호화')
        self.setup_decrypt_tab()
        
        self.tab_control.pack(expand=1, fill="both")
        
        # 상태 표시줄
        self.status_var = tk.StringVar()
        self.status_var.set("준비됨")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_encrypt_tab(self):
        # 암호화 탭 설정
        frame = ttk.LabelFrame(self.encrypt_tab, text="파일/폴더 암호화")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 경로 입력 필드
        ttk.Label(frame, text="암호화할 경로:").grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        self.encrypt_path_entry = ttk.Entry(frame, width=60)
        self.encrypt_path_entry.grid(row=0, column=1, padx=5, pady=10)
        
        # 버튼 프레임
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=0, column=2, padx=5, pady=10)
        
        # 파일 선택 버튼
        ttk.Button(btn_frame, text="파일 선택", command=self.select_file_to_encrypt).pack(side=tk.LEFT, padx=2)
        
        # 폴더 선택 버튼
        ttk.Button(btn_frame, text="폴더 선택", command=self.select_folder_to_encrypt).pack(side=tk.LEFT, padx=2)
        
        # 암호화 옵션 프레임
        options_frame = ttk.LabelFrame(frame, text="암호화 옵션")
        options_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W+tk.E)
        
        # 키 생성 옵션
        ttk.Label(options_frame, text="키 관리:").grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        self.key_option = tk.StringVar(value="new_key")
        ttk.Radiobutton(options_frame, text="새 키 생성", variable=self.key_option, value="new_key").grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(options_frame, text="기존 키 사용", variable=self.key_option, value="existing_key").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 기존 키 선택
        ttk.Label(options_frame, text="개인키 경로:").grid(row=1, column=0, padx=5, pady=10, sticky=tk.W)
        self.private_key_path = ttk.Entry(options_frame, width=50)
        self.private_key_path.grid(row=1, column=1, padx=5, pady=10)
        ttk.Button(options_frame, text="찾기", command=self.select_private_key).grid(row=1, column=2, padx=5, pady=10)
        
        # 암호화 실행 버튼
        ttk.Button(frame, text="암호화 실행", command=self.start_encryption, width=20).grid(row=2, column=0, columnspan=3, pady=20)
        
        # 진행 상황 표시
        self.encrypt_progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=600, mode='indeterminate')
        self.encrypt_progress.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
    
    def setup_decrypt_tab(self):
        # 복호화 탭 설정
        frame = ttk.LabelFrame(self.decrypt_tab, text="파일/폴더 복호화")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 경로 입력 필드
        ttk.Label(frame, text="복호화할 경로:").grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        self.decrypt_path_entry = ttk.Entry(frame, width=60)
        self.decrypt_path_entry.grid(row=0, column=1, padx=5, pady=10)
        
        # 버튼 프레임
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=0, column=2, padx=5, pady=10)
        
        # 파일 선택 버튼
        ttk.Button(btn_frame, text="파일 선택", command=self.select_file_to_decrypt).pack(side=tk.LEFT, padx=2)
        
        # 폴더 선택 버튼
        ttk.Button(btn_frame, text="폴더 선택", command=self.select_folder_to_decrypt).pack(side=tk.LEFT, padx=2)
        
        # 개인키 선택
        ttk.Label(frame, text="개인키 경로:").grid(row=1, column=0, padx=5, pady=10, sticky=tk.W)
        self.decrypt_key_path = ttk.Entry(frame, width=60)
        self.decrypt_key_path.grid(row=1, column=1, padx=5, pady=10)
        ttk.Button(frame, text="찾기", command=self.select_decrypt_key).grid(row=1, column=2, padx=5, pady=10)
        
        # 복호화 실행 버튼
        ttk.Button(frame, text="복호화 실행", command=self.start_decryption, width=20).grid(row=2, column=0, columnspan=3, pady=20)
        
        # 진행 상황 표시
        self.decrypt_progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=600, mode='indeterminate')
        self.decrypt_progress.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
    
    def select_file_to_encrypt(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.encrypt_path_entry.delete(0, tk.END)
            self.encrypt_path_entry.insert(0, file_path)
    
    def select_folder_to_encrypt(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.encrypt_path_entry.delete(0, tk.END)
            self.encrypt_path_entry.insert(0, folder_path)
    
    def select_private_key(self):
        key_path = filedialog.askopenfilename(filetypes=[("PEM 파일", "*.pem"), ("모든 파일", "*.*")])
        if key_path:
            self.private_key_path.delete(0, tk.END)
            self.private_key_path.insert(0, key_path)
    
    def select_file_to_decrypt(self):
        file_path = filedialog.askopenfilename(filetypes=[("암호화된 파일", "*.enc"), ("모든 파일", "*.*")])
        if file_path:
            self.decrypt_path_entry.delete(0, tk.END)
            self.decrypt_path_entry.insert(0, file_path)
    
    def select_folder_to_decrypt(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.decrypt_path_entry.delete(0, tk.END)
            self.decrypt_path_entry.insert(0, folder_path)
    
    def select_decrypt_key(self):
        key_path = filedialog.askopenfilename(filetypes=[("PEM 파일", "*.pem"), ("모든 파일", "*.*")])
        if key_path:
            self.decrypt_key_path.delete(0, tk.END)
            self.decrypt_key_path.insert(0, key_path)
    
    def make_keys(self, key_path=None):
        if key_path and os.path.exists(key_path):
            # 기존 키 사용
            try:
                with open(key_path, "rb") as f:
                    private_key = RSA.import_key(f.read())
                return private_key.publickey().export_key(), private_key.export_key()
            except Exception as e:
                messagebox.showerror("오류", f"키 로드 실패: {e}")
                return None, None
        else:
            # 새 키 생성
            key = RSA.generate(2048)
            private_key = key.export_key()
            public_key = key.publickey().export_key()
            
            # 개인키 저장
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pem",
                filetypes=[("PEM 파일", "*.pem"), ("모든 파일", "*.*")],
                title="개인키 저장 위치"
            )
            
            if not save_path:
                return None, None
                
            with open(save_path, "wb") as f:
                f.write(private_key)
                
            messagebox.showinfo("정보", f"개인키가 저장되었습니다: {save_path}\n\n이 키는 복호화에 필요하니 안전하게 보관하세요!")
            return public_key, private_key
    
    def encrypt_file(self, file_path, rsa_cipher):
        try:
            aes_key = get_random_bytes(32)  # AES 키 생성
            cipher = AES.new(aes_key, AES.MODE_EAX)  # AES 암호화 객체 생성
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            ciphertext, tag = cipher.encrypt_and_digest(file_data)
            enc_aes_key = rsa_cipher.encrypt(aes_key)
            
            with open(file_path + '.enc', 'wb') as enc_file:
                for data in (cipher.nonce, tag, enc_aes_key, ciphertext):
                    enc_file.write(data)
                    
            os.remove(file_path)  # 원본 파일 삭제
            return True
        except Exception as e:
            messagebox.showerror("암호화 오류", f"파일 암호화 실패: {e}")
            return False
    
    def decrypt_file(self, encrypted_file_path, private_key):
        try:
            # 출력 경로 결정
            if encrypted_file_path.endswith('.enc'):
                output_path = encrypted_file_path[:-4]
            else:
                output_path = encrypted_file_path + '.decrypted'
            
            # RSA 복호화 객체 생성
            rsa_cipher = PKCS1_OAEP.new(private_key)
            
            # 암호화된 파일 열기
            with open(encrypted_file_path, 'rb') as enc_file:
                # 파일 구조: nonce(16바이트) + tag(16바이트) + 암호화된 AES 키(256바이트) + 암호화된 데이터
                nonce = enc_file.read(16)
                tag = enc_file.read(16)
                enc_aes_key = enc_file.read(256)
                
                # RSA로 암호화된 AES 키 복호화
                aes_key = rsa_cipher.decrypt(enc_aes_key)
                
                # 암호화된 데이터 읽기
                ciphertext = enc_file.read()
                
                # AES 복호화 객체 생성
                cipher = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
                
                # 데이터 복호화
                data = cipher.decrypt_and_verify(ciphertext, tag)
                
                # 복호화된 데이터를 파일로 저장
                with open(output_path, 'wb') as f:
                    f.write(data)
                
                return True
        except Exception as e:
            messagebox.showerror("복호화 오류", f"파일 복호화 실패: {e}")
            return False
    
    def get_file_paths(self, path):
        if os.path.isfile(path):
            return [path]
        
        file_paths = []
        for root, _, files in os.walk(path):
            for filename in files:
                file_paths.append(os.path.join(root, filename))
        return file_paths
    
    def get_enc_file_paths(self, path):
        if os.path.isfile(path) and path.endswith('.enc'):
            return [path]
        
        file_paths = []
        for root, _, files in os.walk(path):
            for filename in files:
                if filename.endswith('.enc'):
                    file_paths.append(os.path.join(root, filename))
        return file_paths
    
    def encrypt_task(self):
        try:
            path = self.encrypt_path_entry.get()
            
            if not path or not os.path.exists(path):
                messagebox.showerror("오류", "유효한 파일 또는 폴더 경로를 입력하세요.")
                return
            
            # 키 생성 또는 로드
            if self.key_option.get() == "existing_key":
                key_path = self.private_key_path.get()
                if not key_path or not os.path.exists(key_path):
                    messagebox.showerror("오류", "유효한 개인키 파일 경로를 입력하세요.")
                    return
                public_key, _ = self.make_keys(key_path)
            else:
                public_key, _ = self.make_keys()
                
            if public_key is None:
                return
                
            rsa_cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
            
            # 파일 목록 가져오기
            files = self.get_file_paths(path)
            
            if not files:
                messagebox.showinfo("정보", "암호화할 파일이 없습니다.")
                return
            
            # 암호화 진행
            self.encrypt_progress.start()
            success_count = 0
            
            for file_path in files:
                self.status_var.set(f"암호화 중: {file_path}")
                self.root.update_idletasks()
                
                if self.encrypt_file(file_path, rsa_cipher):
                    success_count += 1
            
            self.encrypt_progress.stop()
            self.status_var.set("준비됨")
            
            messagebox.showinfo("완료", f"암호화 완료: {success_count}/{len(files)} 파일 성공")
            
        except Exception as e:
            self.encrypt_progress.stop()
            self.status_var.set("오류 발생")
            messagebox.showerror("오류", f"암호화 중 오류 발생: {e}")
    
    def decrypt_task(self):
        try:
            path = self.decrypt_path_entry.get()
            key_path = self.decrypt_key_path.get()
            
            if not path or not os.path.exists(path):
                messagebox.showerror("오류", "유효한 파일 또는 폴더 경로를 입력하세요.")
                return
                
            if not key_path or not os.path.exists(key_path):
                messagebox.showerror("오류", "유효한 개인키 파일 경로를 입력하세요.")
                return
            
            # 개인키 로드
            try:
                with open(key_path, "rb") as f:
                    private_key = RSA.import_key(f.read())
            except Exception as e:
                messagebox.showerror("오류", f"개인키 로드 실패: {e}")
                return
            
            # 암호화된 파일 목록 가져오기
            files = self.get_enc_file_paths(path)
            
            if not files:
                messagebox.showinfo("정보", "복호화할 파일(.enc)이 없습니다.")
                return
            
            # 복호화 진행
            self.decrypt_progress.start()
            success_count = 0
            
            for file_path in files:
                self.status_var.set(f"복호화 중: {file_path}")
                self.root.update_idletasks()
                
                if self.decrypt_file(file_path, private_key):
                    success_count += 1
            
            self.decrypt_progress.stop()
            self.status_var.set("준비됨")
            
            messagebox.showinfo("완료", f"복호화 완료: {success_count}/{len(files)} 파일 성공")
            
        except Exception as e:
            self.decrypt_progress.stop()
            self.status_var.set("오류 발생")
            messagebox.showerror("오류", f"복호화 중 오류 발생: {e}")
    
    def start_encryption(self):
        threading.Thread(target=self.encrypt_task, daemon=True).start()
    
    def start_decryption(self):
        threading.Thread(target=self.decrypt_task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()
