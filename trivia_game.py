""" Output the request ratio for the last X weeks for PA-UE1 to each service """
import logging
import urllib
import json
from errbot import BotPlugin, botcmd, arg_botcmd
from errbot import botflow, FlowRoot, BotFlow, FLOW_END

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GuessFlows(BotFlow):
    """ Conversation flows related to polls"""

    @botflow
    def guess(self, flow: FlowRoot):
        """ This is a flow that can set a guessing game."""
        # setup Flow
        game_created = flow.connect('trivia', auto_trigger=True, room_flow=True)
        question = game_created.connect('question', predicate=lambda ctx: 'trivias' in ctx)
        one_guess = question.connect('guess')
        one_guess.connect(one_guess)  # loop on itself
        one_guess.connect(FLOW_END, predicate=lambda ctx: 'ended' in ctx)
        game_created.hints = False
        question.hints = False
        one_guess.hints = False


class TriviaGame(BotPlugin):
    """ Trivia Game """
    @botcmd
    def trivia(self, msg, args):
        """ Get trivia questions """
        logger.debug('msg=%s\nargs=%s', msg, args)
        url = 'https://opentdb.com/api.php?amount=10'
        page = urllib.request.Request(url)
        response = json.loads(urllib.request.urlopen(page).read().decode('utf-8'))
        if 'results' in response:
            msg.ctx['trivias'] = response['results']
            return 'Questions Retrieved'
        return 'No questions returned'

    @botcmd
    def question(self, msg, args):
        """ Get a question """
        logger.debug('msg=%s\nargs=%s', msg, args)
        if 'trivias' in msg.ctx:
            msg.ctx['question'] = msg.ctx['trivias'][0]['question']
            msg.ctx['correct_answer'] = msg.ctx['trivias'][0]['correct_answer']
            msg.ctx['incorrect_answers'] = msg.ctx['trivias'][0]['incorrect_answers']
            answers = ''
            for answer in msg.ctx['incorrect_answers']:
                answers = answers + answer + '\n'
            answers = answers + msg.ctx['correct_answer']
            return msg.ctx['question']+'\n'+answers
        logger.info('msg.ctx=%s', msg.ctx)
        return 'Must initialize with trivia command first'

    @arg_botcmd('guess', type=str)
    def guess(self, msg, guess):
        """ Guess """
        if 'trivias' in msg.ctx and 'correct_answer' in msg.ctx:
            if guess == msg.ctx['correct_answer']:
                msg.ctx['ended'] = True
                return 'You got it!'
            else:
                return guess+' was not it'
        logger.info('msg.ctx=%s', msg.ctx)
        return 'Must initialize with trivia command and/or question command first'
