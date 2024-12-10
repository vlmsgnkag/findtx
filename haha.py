import hashlib
import random
import secrets
import os

# Hàm chuyển MD5 thành seed chính xác hơn
def md5_to_seed(md5_hash):
    if len(md5_hash) != 32 or not all(c in "0123456789abcdefABCDEF" for c in md5_hash):
        raise ValueError("MD5 hash không hợp lệ! Nó phải có 32 ký tự hex.")
    seed = int(md5_hash, 16)  # Chuyển đổi MD5 (hex) thành số
    return seed

# Cải tiến phương pháp phân tách MD5 thành nhiều seed để sử dụng cho các RNG khác nhau
def md5_to_multiple_seeds(md5_hash):
    part1 = int(md5_hash[:8], 16)
    part2 = int(md5_hash[8:16], 16)
    part3 = int(md5_hash[16:24], 16)
    part4 = int(md5_hash[24:], 16)
    seed1 = part1 ^ part2
    seed2 = part2 ^ part3
    seed3 = part3 ^ part4
    seed4 = part4 ^ part1
    return seed1, seed2, seed3, seed4

# Mersenne Twister (MT19937)
class MersenneTwister:
    def __init__(self, seed):
        self.state = random.Random(seed)

    def randint(self, min_val, max_val):
        return self.state.randint(min_val, max_val)

# Linear Congruential Generator (LCG)
class LCG:
    def __init__(self, seed, a=1664525, c=1013904223, m=2**32):
        self.state = seed
        self.a = a
        self.c = c
        self.m = m

    def randint(self, min_val, max_val):
        self.state = (self.a * self.state + self.c) % self.m
        return min_val + self.state % (max_val - min_val + 1)

# XorShift RNG
class XorShift:
    def __init__(self, seed):
        self.state = seed

    def randint(self, min_val, max_val):
        self.state ^= (self.state << 13) & 0xFFFFFFFF
        self.state ^= (self.state >> 17) & 0xFFFFFFFF
        self.state ^= (self.state << 5) & 0xFFFFFFFF
        return min_val + (self.state % (max_val - min_val + 1))

# XOR-Shift Add (Biến thể XOR-Shift cải thiện phân phối)
class XorShiftAdd:
    def __init__(self, seed):
        self.state = seed

    def randint(self, min_val, max_val):
        self.state ^= (self.state << 13) & 0xFFFFFFFF
        self.state ^= (self.state >> 17) & 0xFFFFFFFF
        self.state ^= (self.state << 5) & 0xFFFFFFFF
        self.state += 0xDEADBEEF  # Cải thiện phân phối
        return min_val + (self.state % (max_val - min_val + 1))

# Fisher-Yates Shuffle RNG (Thuật toán trộn)
class FisherYatesShuffle:
    def __init__(self, seed):
        self.state = list(range(1, 7))
        random.Random(seed).shuffle(self.state)

    def randint(self, min_val, max_val):
        random.shuffle(self.state)
        return self.state[0]

# SHA-256 Cryptographic RNG (Sử dụng SHA-256 để tạo số ngẫu nhiên bảo mật)
class SHA256RNG:
    def __init__(self, seed):
        self.state = seed.encode('utf-8')

    def randint(self, min_val, max_val):
        hash_val = hashlib.sha256(self.state).hexdigest()
        self.state = hash_val.encode('utf-8')
        return min_val + (int(hash_val, 16) % (max_val - min_val + 1))

# WELL RNG (Well Equidistributed Long-period Linear)
class WELL:
    def __init__(self, seed):
        self.state = seed
        self.n = 624
        self.state_array = [0] * self.n
        self.index = self.n + 1
        self._initialize_state(seed)

    def _initialize_state(self, seed):
        self.state_array[0] = seed
        for i in range(1, self.n):
            self.state_array[i] = (self.state_array[i - 1] ^ (self.state_array[i - 1] >> 30)) + i
        self.index = self.n

    def _twist(self):
        for i in range(self.n):
            y = (self.state_array[i] & 0x80000000) | (self.state_array[(i + 1) % self.n] & 0x7FFFFFFF)
            self.state_array[i] = self.state_array[(i + 397) % self.n] ^ (y >> 1)
            if y % 2 != 0:
                self.state_array[i] ^= 0x9908B0DF
        self.index = 0

    def randint(self, min_val, max_val):
        if self.index >= self.n:
            self._twist()
        y = self.state_array[self.index]
        self.index += 1
        return min_val + (y % (max_val - min_val + 1))

# PCG (Permuted Congruential Generator)
class PCG:
    def __init__(self, seed, a=6364136223846793005, c=1, m=2**64):
        self.state = seed
        self.a = a
        self.c = c
        self.m = m

    def randint(self, min_val, max_val):
        self.state = (self.a * self.state + self.c) % self.m
        return min_val + (self.state % (max_val - min_val + 1))

# Hàm khởi tạo tất cả RNG
def initialize_all_rngs(md5_hash):
    seed1, seed2, seed3, seed4 = md5_to_multiple_seeds(md5_hash)

    mt_rng = random.Random(seed1)  # Mersenne Twister RNG
    crypto_rng = secrets.SystemRandom()  # Cryptographic RNG
    os_rng = os.urandom  # OS-based RNG
    lcg = LCG(seed2)  # Linear Congruential Generator
    xorshift = XorShift(seed3)  # XorShift RNG
    fisher_yates_rng = FisherYatesShuffle(seed4)  # Fisher-Yates Shuffle RNG
    xorshift_add = XorShiftAdd(seed1)  # XOR-Shift Add RNG
    sha256_rng = SHA256RNG(str(seed2))  # SHA-256 Cryptographic RNG
    well_rng = WELL(seed4)  # WELL RNG
    pcg_rng = PCG(seed3)  # PCG RNG

    return mt_rng, crypto_rng, os_rng, lcg, xorshift, fisher_yates_rng, xorshift_add, sha256_rng, well_rng, pcg_rng

# Hàm mô phỏng một phiên chơi Tài Xỉu
def play_game(mt_rng, crypto_rng, os_rng, lcg, xorshift, fisher_yates_rng, xorshift_add, sha256_rng, well_rng, pcg_rng):
    dice_mt = [mt_rng.randint(1, 6) for _ in range(3)]
    total_mt = sum(dice_mt)
    
    dice_crypto = [crypto_rng.randint(1, 6) for _ in range(3)]
    total_crypto = sum(dice_crypto)

    dice_os = [int.from_bytes(os_rng(1), 'big') % 6 + 1 for _ in range(3)]
    total_os = sum(dice_os)

    dice_lcg = [lcg.randint(1, 6) for _ in range(3)]
    total_lcg = sum(dice_lcg)

    dice_xorshift = [xorshift.randint(1, 6) for _ in range(3)]
    total_xorshift = sum(dice_xorshift)

    dice_fisher_yates = [fisher_yates_rng.randint(1, 6) for _ in range(3)]
    total_fisher_yates = sum(dice_fisher_yates)

    dice_xorshift_add = [xorshift_add.randint(1, 6) for _ in range(3)]
    total_xorshift_add = sum(dice_xorshift_add)

    dice_sha256 = [sha256_rng.randint(1, 6) for _ in range(3)]
    total_sha256 = sum(dice_sha256)

    dice_well = [well_rng.randint(1, 6) for _ in range(3)]
    total_well = sum(dice_well)

    dice_pcg = [pcg_rng.randint(1, 6) for _ in range(3)]
    total_pcg = sum(dice_pcg)

    print(f"Mersenne Twister RNG: {dice_mt} (Tổng: {total_mt})")
    print(f"Cryptographic RNG: {dice_crypto} (Tổng: {total_crypto})")
    print(f"OS-based RNG: {dice_os} (Tổng: {total_os})")
    print(f"Linear Congruential Generator: {dice_lcg} (Tổng: {total_lcg})")
    print(f"XorShift RNG: {dice_xorshift} (Tổng: {total_xorshift})")
    print(f"Fisher-Yates Shuffle RNG: {dice_fisher_yates} (Tổng: {total_fisher_yates})")
    print(f"XOR-Shift Add RNG: {dice_xorshift_add} (Tổng: {total_xorshift_add})")
    print(f"SHA-256 RNG: {dice_sha256} (Tổng: {total_sha256})")
    print(f"WELL RNG: {dice_well} (Tổng: {total_well})")
    print(f"PCG RNG: {dice_pcg} (Tổng: {total_pcg})")

    result_mt = "Tài" if total_mt > 10 else "Xỉu"
    result_crypto = "Tài" if total_crypto > 10 else "Xỉu"
    result_os = "Tài" if total_os > 10 else "Xỉu"
    result_lcg = "Tài" if total_lcg > 10 else "Xỉu"
    result_xorshift = "Tài" if total_xorshift > 10 else "Xỉu"
    result_fisher_yates = "Tài" if total_fisher_yates > 10 else "Xỉu"
    result_xorshift_add = "Tài" if total_xorshift_add > 10 else "Xỉu"
    result_sha256 = "Tài" if total_sha256 > 10 else "Xỉu"
    result_well = "Tài" if total_well > 10 else "Xỉu"
    result_pcg = "Tài" if total_pcg > 10 else "Xỉu"

    return result_mt, result_crypto, result_os, result_lcg, result_xorshift, result_fisher_yates, result_xorshift_add, result_sha256, result_well, result_pcg

# Hàm mô phỏng nhiều phiên chơi
def simulate_games(md5_hash, num_games=10000):
    mt_rng, crypto_rng, os_rng, lcg, xorshift, fisher_yates_rng, xorshift_add, sha256_rng, well_rng, pcg_rng = initialize_all_rngs(md5_hash)

    results = {
        "Tài (MT)": 0, "Xỉu (MT)": 0,
        "Tài (Crypto)": 0, "Xỉu (Crypto)": 0,
        "Tài (OS)": 0, "Xỉu (OS)": 0,
        "Tài (LCG)": 0, "Xỉu (LCG)": 0,
        "Tài (XorShift)": 0, "Xỉu (XorShift)": 0,
        "Tài (FisherYates)": 0, "Xỉu (FisherYates)": 0,
        "Tài (XorshiftAdd)": 0, "Xỉu (XorshiftAdd)": 0,
        "Tài (SHA256)": 0, "Xỉu (SHA256)": 0,
        "Tài (WELL)": 0, "Xỉu (WELL)": 0,
        "Tài (PCG)": 0, "Xỉu (PCG)": 0,
    }

    for i in range(num_games):
        print(f"\nPhiên chơi {i + 1}:")
        result_mt, result_crypto, result_os, result_lcg, result_xorshift, result_fisher_yates, result_xorshift_add, result_sha256, result_well, result_pcg = play_game(
            mt_rng, crypto_rng, os_rng, lcg, xorshift, fisher_yates_rng, xorshift_add, sha256_rng, well_rng, pcg_rng)

        results[f"Tài (MT)" if result_mt == "Tài" else f"Xỉu (MT)"] += 1
        results[f"Tài (Crypto)" if result_crypto == "Tài" else f"Xỉu (Crypto)"] += 1
        results[f"Tài (OS)" if result_os == "Tài" else f"Xỉu (OS)"] += 1
        results[f"Tài (LCG)" if result_lcg == "Tài" else f"Xỉu (LCG)"] += 1
        results[f"Tài (XorShift)" if result_xorshift == "Tài" else f"Xỉu (XorShift)"] += 1
        results[f"Tài (FisherYates)" if result_fisher_yates == "Tài" else f"Xỉu (FisherYates)"] += 1
        results[f"Tài (XorshiftAdd)" if result_xorshift_add == "Tài" else f"Xỉu (XorshiftAdd)"] += 1
        results[f"Tài (SHA256)" if result_sha256 == "Tài" else f"Xỉu (SHA256)"] += 1
        results[f"Tài (WELL)" if result_well == "Tài" else f"Xỉu (WELL)"] += 1
        results[f"Tài (PCG)" if result_pcg == "Tài" else f"Xỉu (PCG)"] += 1

    return results

# Hàm hiển thị kết quả tổng hợp và tính tỷ lệ thắng
def display_results(results, num_games):
    total_tai = sum([results[key] for key in results if "Tài" in key])
    total_xiu = sum([results[key] for key in results if "Xỉu" in key])
    
    print(f"Tổng Tài: {total_tai}")
    print(f"Tổng Xỉu: {total_xiu}")
    
    tai_rate = (total_tai / num_games) * 100
    xiu_rate = (total_xiu / num_games) * 100

    if total_tai > total_xiu:
        final_result = "Tài"
    elif total_xiu > total_tai:
        final_result = "Xỉu"
    else:
        final_result = "Hòa"
    
    print(f"\nKết quả cuối cùng: {final_result}")
    print(f"Tỷ lệ thắng của Tài: {tai_rate:.2f}%")
    print(f"Tỷ lệ thắng của Xỉu: {xiu_rate:.2f}%")

# Hàm chính
def main():
    md5_input = input("Nhập chuỗi MD5 để giải mã và phân tích: ").strip()
    
    if len(md5_input) != 32 or not all(c in "0123456789abcdefABCDEF" for c in md5_input):
        print("Chuỗi MD5 không hợp lệ! Vui lòng nhập lại.")
        return

    num_games = int(input("Nhập số phiên chơi (mặc định 10000): ") or 10000)
    
    results = simulate_games(md5_input, num_games)
    
    display_results(results, num_games)

if __name__ == "__main__":
    main()
