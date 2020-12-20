import json
import random
import time

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
VOWELS  = 'AEIOU'
VOWEL_COST  = 250

##################################
##################################
######   DEFINING CLASSES   ######
##################################
##################################
class WOFPlayer():
    def __init__(self, name):
        self.name = name
        self.prizeMoney = 0
        self.prizes = []
        
    def addMoney(self, amt):
        self.prizeMoney += amt
        
    def goBankrupt(self):
        self.prizeMoney = 0
        
    def addPrize(self, price):
        self.prizes.append(price)
        
    def __str__(self):
        return '{} (${})'.format(self.name, self.prizeMoney)


class WOFHumanPlayer(WOFPlayer):
    """ The human player should always be prompted to make their next move """
    def getMove(self, category, obscuredPhrase, guessed):
        human_player_move = showBoard(category, obscuredPhrase, guessed)
        human_player_prompt = input(human_player_move)
        return human_player_prompt
        

class WOFComputerPlayer(WOFPlayer):
    """ 
    The computer player would not need to see a prompt for their next move.
    Instead, they should make their move based on the difficulty set by the human player at the beginning of the game
    """
    #this is a list of english characters in ascending order of frequency
    SORTED_FREQUENCIES = 'ZQXJKVBPYGFWMUCLDRHSNIOATE'
    
    #defining an additional constructor for the computer class to handle the game difficulty
    def __init__(self, name, difficulty):
        WOFPlayer.__init__(self, name)
        self.difficulty = difficulty
        
    #this method decides whether to make a good move or not
    def smartCoinFlip(self):
        random_number = random.randint(1, 10)
        if random_number > self.difficulty:
            return True
        else:
            return False
    
    #this method prevents the computer from guessing already guessed letters
    # it also removes vowels from the list of possible letters if the computer player doesn't have enough money
    # -to guess a vowel
    def getPossibleLetters(self, guessed):
        possible_letters = []
        for char in LETTERS:
            if char not in guessed:
                possible_letters.append(char)
    
        if self.prizeMoney < VOWEL_COST:
                for vowel in VOWELS:
                    vowel_char_count = possible_letters.count(vowel)
                    for _ in range(vowel_char_count):
                        possible_letters.remove(vowel)
        return possible_letters
    
    #calls the smartCoinFlip() method to make a valid move for the computer player
    def getMove(self, category, obscuredPhrase, guessed):
        possible_letters = self.getPossibleLetters(guessed)
        if len(possible_letters) < 1:
            return 'pass'
        smart_flip = self.smartCoinFlip()
        
        if smart_flip == True:
            for lett in possible_letters:
                if lett in self.SORTED_FREQUENCIES:
                    return lett
        else:
            return random.choice(possible_letters)
    


##################################
##################################
######      FUNCTIONS       ######
##################################
##################################
# Repeatedly asks the user for a number between min & max (inclusive)
def getNumberBetween(prompt, min, max):
    userinp = input(prompt) # ask the first time

    while True:
        try:
            n = int(userinp) # try casting to an integer
            if n < min:
                errmessage = 'Must be at least {}'.format(min)
            elif n > max:
                errmessage = 'Must be at most {}'.format(max)
            else:
                return n
        except ValueError: # The user didn't enter a number
            errmessage = '{} is not a number.'.format(userinp)

        # If we haven't gotten a number yet, add the error message
        # and ask again
        userinp = input('{}\n{}'.format(errmessage, prompt))


# Spins the wheel of fortune wheel to give a random prize
# Examples:
#    { "type": "loseturn", "text": "loses a turn", "prize": false }
def spinWheel():
    with open("prizes.json") as prizes_file:
        prize_contents = json.loads(prizes_file.read())
    num_of_prizes = len(prize_contents['prizes'])
    found_prize = prize_contents['prizes'][random.randrange(num_of_prizes)]
    return found_prize


# Returns a category & phrase (as a tuple) to guess
# Example:
#     ("Artist & Song", "Whitney Houston's I Will Always Love You")
def getRandomCategoryAndPhrase():
    with open('phrases.json', 'r') as phrase_file:
        phrase_contents = json.loads(phrase_file.read())
    num_of_phrases = len(phrase_contents['phrases'])
    found_phrase = phrase_contents['phrases'][random.randrange(num_of_phrases)]
    return found_phrase['Category'], found_phrase['Phrase'].upper()


# Given a phrase and a list of guessed letters, returns an obscured version
# Example:
#     guessed: ['L', 'B', 'E', 'R', 'N', 'P', 'K', 'X', 'Z']
#     phrase:  "GLACIER NATIONAL PARK"
#     returns> "_L___ER N____N_L P_RK"
def obscurePhrase(phrase, guessed):
    rv = ''
    for s in phrase:
        if (s in LETTERS) and (s not in guessed):
            rv = rv+'_'
        else:
            rv = rv+s
    return rv


# Returns a string representing the current state of the game
def showBoard(category, obscuredPhrase, guessed):
    return """
Category: {}
Phrase:   {}
Guessed:  {}
{} has ${}. Make a guess... """.format(category, obscuredPhrase, ', '.join(sorted(guessed)), player.name, player.prizeMoney)




##################################
##################################
######   GAME LOGIC CODE    ######
##################################
##################################
print('='*15)
print('WHEEL OF PYTHON')
print('='*15)
print('')

num_human = getNumberBetween('How many human players? ', 0, 10)

# Create the human player instances
human_players = [WOFHumanPlayer(input('Enter the name for human player #{}: '.format(i+1))) for i in range(num_human)]

num_computer = getNumberBetween('How many computer players:? ', 0, 10)

# If there are computer players, ask how difficult they should be
if num_computer >= 1:
    difficulty = getNumberBetween('What difficulty for the computers? (1-10): ', 1, 10)

# Create the computer player instances
computer_players = [WOFComputerPlayer('Computer {}'.format(i+1), difficulty) for i in range(num_computer)]

players = human_players + computer_players

#no players no game
if len(players) == 0:
    print('We need players to play!')
    raise Exception('Not enough players')


# category and phrase are strings.
category, phrase = getRandomCategoryAndPhrase()
# guessed is a list of the letters that have been guessed
guessed = []

# playerIndex keeps track of the index (0 to len(players)-1) of the player whose turn it is
playerIndex = 0

# will be set to the player instance when/if someone wins
winner = False

def requestPlayerMove(player, category, guessed):
    while True: # keep asking the player for a move until they give a valid one
        time.sleep(0.1) # added so that any feedback is printed out before the next prompt

        move = player.getMove(category, obscurePhrase(phrase, guessed), guessed)
        move = move.upper() # convert whatever the player entered to UPPERCASE
        if move == 'EXIT' or move == 'PASS':
            return move
        elif len(move) == 1: # they guessed a character
            if move not in LETTERS: # the user entered an invalid letter (such as @, #, or $)
                print('Guesses should be letters. Try again.')
                continue
            elif move in guessed: # this letter has already been guessed
                print('{} has already been guessed. Try again.'.format(move))
                continue
            elif move in VOWELS and player.prizeMoney < VOWEL_COST: # if it's a vowel, we need to be sure the player has enough
                    print('Need ${} to guess a vowel. Try again.'.format(VOWEL_COST))
                    continue
            else:
                return move
        else: # they guessed the phrase
            return move


while True:
    player = players[playerIndex]
    wheelPrize = spinWheel()

    print('')
    print('-*-'*15)
    print(showBoard(category, obscurePhrase(phrase, guessed), guessed))
    print('')
    print('{} spins...'.format(player.name))
    time.sleep(3) # pause for dramatic effect!
    print('{}!'.format(wheelPrize['text']))
    time.sleep(1) # pause again for more dramatic effect!

    if wheelPrize['type'] == 'bankrupt':
        player.goBankrupt()
    elif wheelPrize['type'] == 'loseturn':
        pass # do nothing; just move on to the next player
    elif wheelPrize['type'] == 'cash':
        move = requestPlayerMove(player, category, guessed)
        if move == 'EXIT': # leave the game
            print('Until next time!')
            break
        elif move == 'PASS': # will just move on to next player
            print('{} passes'.format(player.name))
        elif len(move) == 1: # they guessed a letter
            guessed.append(move)

            print('{} guesses "{}"'.format(player.name, move))
            print("Checking if there's {} in the phrase...".format(move))
            time.sleep(2)


            if move in VOWELS:
                player.prizeMoney -= VOWEL_COST

            count = phrase.count(move) # returns an integer with how many times this letter appears
            if count > 0:
                if count == 1:
                    print("There is one {}".format(move))
                else:
                    print("There are {} {}'s".format(count, move))

                # Give them the money and the prizes
                player.addMoney(count * wheelPrize['value'])
                if wheelPrize['prize']:
                    player.addPrize(wheelPrize['prize'])

                # all of the letters have been guessed
                if obscurePhrase(phrase, guessed) == phrase:
                    winner = player
                    break

                continue # this player gets to go again

            elif count == 0:
                print("There is no {}".format(move))
        else: # they guessed the whole phrase
            if move == phrase: # they guessed the full phrase correctly
                winner = player

                # Give them the money and the prizes
                player.addMoney(wheelPrize['value'])
                if wheelPrize['prize']:
                    player.addPrize(wheelPrize['prize'])

                break
            else:
                print('{} was not the phrase'.format(move))

    # Move on to the next player (or go back to player[0] if we reached the end)
    playerIndex = (playerIndex + 1) % len(players)


if winner:
    # In your head, you should hear this as being announced by a game show host
    print("\n\n====================\n")
    print('{} wins! The phrase was {}'.format(winner.name, phrase))
    print('{} won ${}'.format(winner.name, winner.prizeMoney))
    print("\n====================")
    if len(winner.prizes) > 0:
        print('{} also won:'.format(winner.name))
        for prize in winner.prizes:
            print('    - {}'.format(prize))
else:
    print('Nobody won. The phrase was {}'.format(phrase))