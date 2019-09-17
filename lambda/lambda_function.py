# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
from ask_sdk_model.slu.entityresolution import StatusCode
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

from api import SumoAPI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome, you can run a search or ask for help"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )



class SavedSearchIntentHandler(AbstractRequestHandler):
    
    @staticmethod
    def get_slot_values(filled_slots):
        """Return slot values with additional info."""
        slot_values = {}
        logger.info("Filled slots: {}".format(filled_slots).replace("\n", "\r"))
    
        for key, slot_item in six.iteritems(filled_slots):
            name = slot_item.name
            try:
                status_code = slot_item.resolutions.resolutions_per_authority[0].status.code
    
                if status_code == StatusCode.ER_SUCCESS_MATCH:
                    slot_values[name] = {
                        "synonym": slot_item.value,
                        "resolved": slot_item.resolutions.resolutions_per_authority[0].values[0].value.__dict__,  # to make it JSON serializable
                        "is_validated": True,
                    }
                elif status_code == StatusCode.ER_SUCCESS_NO_MATCH:
                    slot_values[name] = {
                        "synonym": slot_item.value,
                        "resolved": slot_item.value,
                        "is_validated": False,
                    }
                else:
                    pass
            except (AttributeError, ValueError, KeyError, IndexError, TypeError) as e:
                # for BUILT-IN intents, there are no resolutions, but the value is specified
                if slot_item.value is not None and slot_item.value != 'NONE':
                    slot_values[name] = {
                        "synonym": slot_item.value,
                        "resolved": slot_item.value,
                        "is_validated": True,
                    }
                else:
                    logger.info("SLOT {} UNRESOLVED".format(name))
                    slot_values[name] = {
                        "synonym": slot_item.value,
                        "resolved": slot_item.value,
                        "is_validated": False,
                    }
        return slot_values
        
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RunSearch")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        sumoapi = SumoAPI("suNJV499XriL61", "Pq5FOo4FDykMwo4HA8ZQFIs5CsfVHIcuneonQtFqrUQu3K72uAzLTkw7XKSKM9zk", "nite", handler_input.request_envelope)
        logger.info(handler_input.request_envelope)
        params = self.get_slot_values(handler_input.request_envelope.request.intent.slots)
        logger.info("Params %s" % params)
        speak_output = sumoapi.run_raw_search("_sourceCategory=%s*" % params["search"])
        # speak_output = "Job Scheduled"
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SavedSearchIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())
# sb.withR
lambda_handler = sb.lambda_handler()

