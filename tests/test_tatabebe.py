import random
class RandomNumberGame:
    def __init__(self):
        self.number = random.randint(1, 10)
        self._lower_text = "Мое число меньше!"
        self._higher_text = "Мое число больше!"
        self._correct_text = "Ты отгадал!"

    def _guess(self, number: int):
        if number < self.number:
            return self._higher_text
        elif number > self.number:
            return self._lower_text
        else:
            return self._correct_text
    
    def play(self):
        while True:
            number = int(input("Введите число от 1 до 10: "))
            result = self._guess(number)
            print(result)
            if result == self._correct_text:
                break

game = RandomNumberGame()
game.play()