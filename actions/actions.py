import random
import urllib.parse
from typing import Any, Text, Dict, List
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

"""
These are the todos: -
[x]: Make the feedback form reach the devs via email.
[ ]: Add the Weather API and get the actual weather of the locations.
[x]: Edit the code in here to properly send weather data.
[ ]: Create a new bot from scratch taking ideas from here and turn that one into a support assistant bot for every product that we build from now on.
"""


class ValidateFeedbackForm(FormValidationAction):
    """
    This class is responsible for validating the inputs of the feedback form.

    The inputs include:
        1. Name
            - Returns the recieved input if it is not empty.
            - Returns null if the name is empty.
        2. Function
            - Returns the recieved input if it is not empty.
            - Returns null if the function is empty.
        3. Feedback
            - Returns the recieved input if it is not empty.
            - Returns null if the feedback is empty.
    """

    functions = ["weather", "feedback"]

    def name(self) -> Text:
        """
        Returns the name of the form.
        """

        return "validate_feedback_form"

    def validate_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """
        Validates the name input.
        """

        if slot_value:
            return {"name": slot_value}
        else:
            dispatcher.utter_message(
                "Sorry, I didn't get any name. Please enter in the following format: -\nFormat: 'My name is <name>'"
            )
            return {"name": None}

    def validate_rating(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """
        Validates the rating input.
        """
        try:
            if (
                slot_value
                and int(slot_value)
                and int(slot_value) >= 1
                and int(slot_value) <= 5
            ):
                if int(slot_value) < 3:
                    dispatcher.utter_message(
                        "I am really sorry for the bad experience. I will make sure to improve."
                    )
                return {"rating": slot_value}
            else:
                dispatcher.utter_message(
                    "Sorry, I didn't get any rating. Please note that the rating must be in integer form and between 1 and 5 (both inclusive)"
                )
            return {"rating": None}
        except ValueError:
            dispatcher.utter_message(
                "Sorry, I didn't get any rating. Please note that the rating must be in integer form and between 1 and 5 (both inclusive)"
            )
            return {"rating": None}

    def validate_function(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """
        Validates the function input.
        """

        if slot_value and str(slot_value).lower() in self.functions:
            return {"function": slot_value}
        else:
            options = ", ".join(self.functions)
            dispatcher.utter_message(
                f"Sorry, I didn't get any function. Please note that it has to be one of the following: -\n{options}"
            )
            return {"function": None}

    def validate_feedback(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """
        Validates the feedback input.
        """

        if slot_value:
            return {"feedback": slot_value}
        else:
            dispatcher.utter_message(
                "Sorry, I didn't get any feedback. Please enter in the following format: -\nFormat: 'My feedback is <feedback>'"
            )
            return {"feedback": None}


class ActionSendFeedback(Action):
    """
    This class is responsible for sending the feedback to the devs.
    """

    def name(self) -> Text:
        return "action_send_feedback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List:
        print("I am in run")
        try:
            s = smtplib.SMTP("smtp.gmail.com", 587)
            s.starttls()
            s.login(os.getenv("GMAIL_ACC"), os.getenv("GMAIL_PASS"))
            print("login complete")
        except Exception as e:
            print(e)
            dispatcher.utter_message(
                'Sorry, I was unable to send the feedback. Please mail the feedback to my devs on "contact.bhaibot@gmail.com"'
            )
            s.quit()
            return [
                SlotSet("function", None),
                SlotSet("feedback", None),
                SlotSet("rating", None),
            ]
        name = tracker.get_slot("name")
        function = tracker.get_slot("function")
        feedback = tracker.get_slot("feedback")
        print(name, function, feedback)

        if name and function and feedback:
            print("I am in the function with all slots not-None")
            try:
                mail = MIMEMultipart()
                mail["From"] = os.getenv("GMAIL_ACC")
                mail["To"] = "contact.bhaibot@gmail.com"
                mail["Subject"] = f"Feedback for {function} from {name}"
                body = (
                    "Name: "
                    + name
                    + "\nFunction: "
                    + function
                    + "\nFeedback: "
                    + feedback
                )
                mail.attach(MIMEText(body, "plain"))
                s.sendmail(
                    os.getenv("GMAIL_ACC"),
                    "contact.bhaibot@gmail.com",
                    mail.as_string(),
                )
                dispatcher.utter_message(
                    "Thank you for sharing your valuable feedback. I have shared it with the devs."
                )
            except Exception as e:
                print(e)
                dispatcher.utter_message(
                    'Sorry, I was unable to send the feedback. Please mail the feedback to my devs on "contact.bhaibot@gmail.com"'
                )

        else:
            dispatcher.utter_message(
                'Sorry, I was unable to send the feedback. Please mail the feedback to my devs on "contact.bhaibot@gmail.com"'
            )
        s.quit()
        print("Exiting function")
        return [
            SlotSet("function", None),
            SlotSet("feedback", None),
            SlotSet("rating", None),
        ]


class ActionGetWeather(Action):
    """
    [x]: Edit the code in here to properly send weather data.
    [ ]: Add the Weather API and get the actual weather of the locations.
    """

    gifs4weather = {
        20: "https://media.giphy.com/media/s4Bi420mMDRBK/giphy.gif",
        25: "https://media.giphy.com/media/St3ltqQwRGuKvX7nM6/giphy.gif",
        30: "https://media.giphy.com/media/5xtDarIN81U0KvlnzKo/giphy.gif",
        35: "https://media.giphy.com/media/8YxIlxkPKuRsz0ypaP/giphy.gif",
        40: "https://media.giphy.com/media/xT0Gqz4x4eLd5gDtaU/giphy.gif",
    }

    tags4weather = {
        20: "cold",
        25: "warm",
        30: "hot",
        35: "very hot",
        40: "enough to fry humans",
    }

    def name(self) -> Text:
        return "action_get_weather"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        temp = random.randint(15, 45)
        print(temp)
        if temp in self.gifs4weather.keys():
            gif = self.gifs4weather[temp]
            tag = self.tags4weather[temp]
        else:
            if temp < 20:
                gif = self.gifs4weather[20]
                tag = self.tags4weather[20]
            elif temp > 40:
                gif = self.gifs4weather[40]
                tag = self.tags4weather[40]
            else:
                for temperature in self.gifs4weather.keys():
                    if temp < temperature:
                        gif = self.gifs4weather[temperature - 5]
                        tag = self.tags4weather[temperature - 5]
                        break
        if location:
            dispatcher.utter_message(
                text=f"The weather in {location} is {tag}.",
                image=gif,
            )
        else:
            dispatcher.utter_message(
                text="Sorry, I don't know the weather in that location."
            )

        return [SlotSet("location", "")]


class ValidateWeatherForm(FormValidationAction):
    """
    This class is resposible for validating the inputs of the weather form.

    The inputs include:
        1. Location
            - Returns the recieved input if it is not empty and the regex pattern is able to extract the location from the message.
            - Returns null if the location is not identified.

    """

    def name(self) -> Text:
        """
        Returns the name of the form.
        """

        return "validate_weather_form"

    def validate_location(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """
        Validates the location input.
        """

        if slot_value:
            return {"location": slot_value}
        else:
            dispatcher.utter_message(
                "Sorry, I didn't get any location. Please enter in the following format: -\nFormat: 'weather in <location>'"
            )
            return {"location": None}


class ActionGenerateSearch(Action):
    """
    This class is responsible for generating the search link based on the search engine the user chooses.
    """

    search_engines = {
        "google": "https://www.google.com/search?q=",
        "stackoverflow": "https://stackoverflow.com/search?q=",
        "youtube": "https://www.youtube.com/results?search_query=",
        "bing": "https://www.bing.com/search?q=",
        "github": "https://www.github.com/search?q=",
    }

    def query_to_url(self, query: Text, search_engine: Text) -> Text:
        """
        This method generates the url for the query passed in.
        """
        if search_engine not in self.search_engines:
            raise ValueError(f"Search engine {search_engine} is not supported.")
        return self.search_engines[search_engine] + urllib.parse.quote_plus(query)

    def name(self) -> Text:
        return "action_generate_search"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        search_engine = tracker.get_slot("search_engine")
        query = tracker.get_slot("query")
        if search_engine and query:
            try:
                url = self.query_to_url(query, search_engine)
                dispatcher.utter_message(
                    text=f"Here is what I found for {query} on {search_engine}: {url}"
                )
            except ValueError as e:
                dispatcher.utter_message(text=str(e))

        else:
            dispatcher.utter_message(text="Sorry, I don't know what to search for.")

        return [SlotSet("search_engine", ""), SlotSet("query", "")]


class ValidateSearchForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_search_form"

    def validate_search_engine(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value.lower() in ActionGenerateSearch.search_engines.keys():
            return {"search_engine": slot_value.lower()}
        else:
            dispatcher.utter_message(response="utter_search_engine_not_supported")
            return {"search_engine": None}

    def validate_query(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value:
            return {"query": slot_value}
        else:
            dispatcher.utter_message("Sorry, I didn't get any query.")
            return {"query": None}
