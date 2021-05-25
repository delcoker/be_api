# import flair
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentApi:
    def __init__(self) -> None:
        self.analyzer = SentimentIntensityAnalyzer()
        # self.flair_sentiment = flair.models.TextClassifier.load("en-sentiment")

    def getSentiment(self, text):
        """
        positive sentiment: compound score >= 0.05
        neutral sentiment: (compound score > -0.05) and (compound score < 0.05)
        negative sentiment: compound score <= -0.05
        """
        scores = self.analyzer.polarity_scores(text)
        # s = flair.data.Sentence(text)
        # self.flair_sentiment.predict(s)
        score = scores["compound"]
        sentiment = None

        if score >= 0.05:
            sentiment = "POSITIVE"
        elif score > -0.05 < 0.05:
            sentiment = "NEUTRAL"
        elif score <= -0.05:
            sentiment = "NEGATIVE"

        result = {"score": score, "sentiment": sentiment}

        print("{:-<65} {}".format(text, result))
        return result

    def test(self):
        sentences = [
            "VADER is smart, handsome, and funny.",  # positive sentence example
            "VADER is smart, handsome, and funny!",  # punctuation emphasis handled correctly (sentiment intensity adjusted)
            "VADER is very smart, handsome, and funny.",  # booster words handled correctly (sentiment intensity adjusted)
            "VADER is VERY SMART, handsome, and FUNNY.",  # emphasis for ALLCAPS handled
            "VADER is VERY SMART, handsome, and FUNNY!!!",  # combination of signals - VADER appropriately adjusts intensity
            "VADER is VERY SMART, uber handsome, and FRIGGIN FUNNY!!!",  # booster words & punctuation make this close to ceiling for score
            "VADER is not smart, handsome, nor funny.",  # negation sentence example
            "The book was good.",  # positive sentence
            "At least it isn't a horrible book.",  # negated negative sentence with contraction
            "The book was only kind of good.",  # qualified positive sentence is handled correctly (intensity adjusted)
            "The plot was good, but the characters are uncompelling and the dialog is not great.",  # mixed negation sentence
            "Today SUX!",  # negative slang with capitalization emphasis
            "Today only kinda sux! But I'll get by, lol",  # mixed sentiment example with slang and constrastive conjunction "but"
            "Make sure you :) or :D today!",  # emoticons handled
            "Catch utf-8 emoji such as such as 💘 and 💋 and 😁",  # emojis handled
            "Not bad at all",  # Capitalized negation
        ]

        for sentence in sentences:
            self.getSentiment(sentence)


x = SentimentApi()
x.test()