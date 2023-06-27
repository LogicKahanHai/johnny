import urllib.parse
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionGetWeather(Action):

    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        location = tracker.get_slot("location")
        if location:
            dispatcher.utter_message(text=f"The weather in {location} is sunny.", elements=[{
                "title": "Sunny",
                "image_url": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__340.jpg",
                "subtitle": "It is 30 degrees celcius.",
                "buttons": [
                    {
                        "title": "More info",
                        "url": "https://www.google.com/search?q=weather+in+" + urllib.parse.quote_plus(location),
                        "type": "web_url"
                    }
                ]
            }])
        else:
            dispatcher.utter_message(text="Sorry, I don't know the weather in that location.")

        return [SlotSet("location", "")]


class ValidateWeatherForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_weather_form"

    def validate_location(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value:
            return {"location": slot_value}
        else:
            dispatcher.utter_message(
                "Sorry, I didn't get any location. Please enter in the following format: -\nFormat: 'weather in <location>'")
            return {"location": None}


class ActionGenerateSearch(Action):
    search_engines = {
        "google": "https://www.google.com/search?q=",
        "stackoverflow": "https://stackoverflow.com/search?q=",
        "youtube": "https://www.youtube.com/results?search_query=",
        "bing": "https://www.bing.com/search?q=",
        "github": "https://www.github.com/search?q="
    }

    def query_to_url(self, query: Text, search_engine: Text) -> Text:
        if search_engine not in self.search_engines:
            raise ValueError(f"Search engine {search_engine} is not supported.")
        return self.search_engines[search_engine] + urllib.parse.quote_plus(query)

    def name(self) -> Text:
        return "action_generate_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        search_engine = tracker.get_slot("search_engine")
        query = tracker.get_slot("query")
        if search_engine and query:
            try:
                url = self.query_to_url(query, search_engine)
                dispatcher.utter_message(text=f"Here is what I found for {query} on {search_engine}: {url}")
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
