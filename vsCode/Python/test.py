import random

def updown_game():
    answer = random.randint(1, 100)
    tries = 0

    print("1부터 100 사이 숫자를 맞춰보세요!")

    while True:
        tries += 1
        guess = input("숫자 입력: ")

        if not guess.isdigit():
            print("숫자를 입력하세요!")
            continue

        guess = int(guess)

        if guess < answer:
            print("UP!")
        elif guess > answer:
            print("DOWN!")
        else:
            print(f"정답! {tries}번 만에 맞췄어요!")
            break

if __name__ == "__main__":
    updown_game()