"""
A module for the narrative class.
"""


import json


class Narrative:
    def __init__(self):
        self.id = None
        self.title = None
        self.synopsis = None
        self.setting = None


class NarrativeEncoder(json.JSONEncoder):
    def default(self, o):
        d = {}
        d["storyId"] = o.id
        d["storyTitle"] = o.title
        d["synopsis"] = o.synopsis
        d["setting"] = o.setting
        d["documentId"] = "settings"
        return d


class NarrativeDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        n = Narrative()

        if "storyId" in d:
            n.id = d["storyId"]
        if "storyTitle" in d:
            n.title = d["storyTitle"]
        if "synopsis" in d:
            n.synopsis = d["synopsis"]
        if "setting" in d:
            n.setting = d["setting"]

        return n


def get_narrative_from_json(json_data: str) -> Narrative:
    return json.loads(json_data, cls=NarrativeDecoder)
