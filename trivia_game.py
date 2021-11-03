""" Output the request ratio for the last X weeks for PA-UE1 to each service """
import logging
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
        one_guess = game_created.connect('guess')
        one_guess.connect(one_guess)  # loop on itself
        one_guess.connect(FLOW_END, predicate=lambda ctx: 'ended' in ctx)
        game_created.hints = False
        one_guess.hints = False


class TriviaGame(BotPlugin):
    """ Trivia Game """
    @botcmd
    def trivia(self, msg, args):
        """ Get trivia questions """
        logger.debug('msg=%s\nargs=%s', msg, args)
        trivias = []
        trivias.append({'question': 'blah', 'incorrect': ['boo', 'hoo'], 'correct': ['bin']})
        msg.ctx['trivias'] = trivias
        return 'Questions Retrieved'

    @arg_botcmd('guess', type=str)
    def guess(self, msg, guess):
        """ Guess """
        if 'trivias' in msg.ctx:
            if guess == 'foo':
                msg.ctx['ended'] = True
                return 'You got it!'
            else:
                return guess+' was not it'
        return 'Must initialize with trivia command first'