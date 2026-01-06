"""Shared constants for JereChat."""

# Model identifiers
MODEL_15PRO = "1.5pro"
MODEL_RAMPION2 = "rampion2"

# Rampion 2 model checkpoint path
DEFAULT_CHECKPOINT_PATH = "data/save/cb_model/corpus/2-2_500/2000_checkpoint.tar"

# Token constants for Rampion 2 model
PAD_TOKEN = 0
SOS_TOKEN = 1
EOS_TOKEN = 2
MAX_LENGTH = 10

# UI suggestion prompts
SUGGESTIONS = {
    ":blue[:material/door_open:] Knock Knock!": "Play Knock Knock",
    ":green[:material/sentiment_very_satisfied:] Tell a joke": "Tell a joke",
    ":orange[:material/draft:] Write an essay": "Write an essay",
    ":violet[:material/code:] Write some code": "Write some code",
    ":red[:material/skillet:] Cook JereChat": "I'm gonna cook you",
}
