import pandas as pd


non_shark_families = [
    "Dasyatidae",
    "Mobulidae",
    "Myliobatidae",
    "Rajidae",
    "Torpedinidae",
]


def catch_count(df: pd.DataFrame, fate: str, med_weight: float) -> int:
    """
    Calculate the number of individual sharks from total catch amounts.

    Parameters
    ----------
    df: pd.DataFrame
        Data for either coastal or offshore shark species.
    fate: str
        The fate for which mortality is being calculated.
        Allowed values: ["discard_alive", "discard_dead", "retained"]
    med_weight: float
        Median weight of coastal or offshore shark species.
    Returns
    -------
    catch_count: int
        The number of individual sharks caught.
    """
    if fate == "retained":
        total_catch = df[df.catch_type == "Landings"]["sum"].sum()
    else:
        total_catch = df[df.catch_type == "Discards"]["sum"].sum()
    return int(total_catch * 1000 / med_weight)


def p_fate(fate_df: pd.DataFrame, fate: str, domain: str) -> float:
    """
    Calculate the probability of the given fate for either coastal or offshore species.

    Parameters
    ----------
    fate_df: pd.DataFrame
        The fate dataset to calculate fate proababilities.
    fate: str
        The fate to calculate probability for.
        Allowed values: ["discard_alive", "discard_dead", "retained"]
    domain: str
        Allowed values: ["coastal", "offshore"]

    Returns
    -------
    p_fate: float
        The probability of the given fate.
    """
    fate_shark = fate_df[~fate_df.family.isin(non_shark_families)]
    if domain == "coastal":
        fate_non_rfmo_shark = fate_shark[fate_shark.rfmo == "Non-RFMO"]
    else:
        fate_non_rfmo_shark = fate_shark[fate_shark.rfmo != "Non-RFMO"]

    # Probabilities of each fate
    fate_probs = (
            fate_non_rfmo_shark.groupby(["fate_type"])["sample_size"].sum()
            / fate_non_rfmo_shark.groupby(["fate_type"])["sample_size"].sum().sum()
    )

    # Probability of given fate
    if (fate == "retained") and (domain == "coastal"):
        p = fate_probs.iloc[-2:].sum()
    elif (fate == "retained") and (domain == "offshore"):
        p = fate_probs.loc["retained_whole"]
    else:
        p = fate_probs[fate_probs.index == fate].values[0]
    return p


def m_fate(mortality_df: pd.DataFrame, fate: str, domain: str) -> float:
    """
    Calculate the mortality of the given fate for either coastal or offshore species.

    Parameters
    ----------
    mortality_df: pd.DataFrame
        The mortality dataset to calculate fate mortality probabilities.
    fate: str
        The fate to calculate mortality probability for.
        Allowed values: ["discard_alive", "discard_dead", "retained"]
    domain: str
        Allowed values: ["coastal", "offshore"]

    Returns
    -------
    p_fate: float
        The probability of mortality for the given fate.
    """
    mortality_shark = mortality_df[~mortality_df.family.isin(non_shark_families)]
    # Probability of each post release event
    post_release_probs = (
            mortality_shark.groupby("estimate_type").sample_size.sum()
            / mortality_shark.groupby("estimate_type").sample_size.sum().sum()
    )
    # Probability of the given mortality
    if fate == "discard_alive":
        mortality_prob = post_release_probs[post_release_probs.index == "post-release mortality"].values[0]
    elif fate in ["discard_dead", "retained"]:
        mortality_prob = 1
    else:
        raise TypeError(f"fate='{fate}' not understood!")
    return mortality_prob

