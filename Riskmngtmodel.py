import pandas as pd
import numpy as np

# Defining the investment stages and their outcome distributions
STAGES = ['Pre-seed', 'Seed', 'Post-seed', 'Series A']
OUTCOME_DISTRIBUTIONS = {
    'Pre-seed': {'mean': 0.8, 'stddev': 0.5},
    'Seed': {'mean': 1.2, 'stddev': 0.6},
    'Post-seed': {'mean': 1.6, 'stddev': 0.7},
    'Series A': {'mean': 2.0, 'stddev': 0.8},
}

# Global variables
CAPITAL = 10**6  # starting capital
MANAGEMENT_FEE = 0.02  # 2%
YEARS = 10

class VentureCapital:
    def __init__(self, initial_capital, management_fee):
        self.capital = initial_capital
        self.management_fee = management_fee
        self.investments = []  # investments that have not yet matured
        self.yearly_investments = []  # for tracking
        self.yearly_returns = []  # for tracking
        self.distributions_to_lps = 0  # total distributions to LPs
        self.carry = 0.2  # carried interest
        self.preferred_return = 0.08  # preferred return rate

    def invest(self, year, strategy):
        for stage in STAGES:
            allocation = strategy.loc[year, stage]
            investment_amount = allocation * self.capital
            self.capital -= investment_amount
            self.yearly_investments.append((year, stage, investment_amount))

            outcome_year = year + np.random.randint(4, 7)  # 4-6 years in the future
            self.investments.append((outcome_year, investment_amount, stage))

    def observe_outcomes(self, year):
        for i in reversed(range(len(self.investments))):  # iterating in reversed order because we're deleting
            outcome_year, investment_amount, stage = self.investments[i]
            if year >= outcome_year:
                outcome_distribution = OUTCOME_DISTRIBUTIONS[stage]
                return_ = np.random.normal(outcome_distribution['mean'], outcome_distribution['stddev']) * investment_amount
                self.yearly_returns.append((year, return_))

                # Calculate distributions using the waterfall structure
                return_of_capital = min(return_, investment_amount)
                return_ -= return_of_capital
                self.distributions_to_lps += return_of_capital

                preferred_return = min(return_, investment_amount * self.preferred_return)
                return_ -= preferred_return
                self.distributions_to_lps += preferred_return

                if self.distributions_to_lps < self.capital * (1 - self.carry):  # Catch-up
                    catch_up = min(return_, self.capital * (1 - self.carry) - self.distributions_to_lps)
                    return_ -= catch_up
                    self.distributions_to_lps += catch_up
                
                profit_sharing = return_
                self.distributions_to_lps += profit_sharing * (1 - self.carry)  # LPs' share
                self.capital += profit_sharing * self.carry  # GP's share

                del self.investments[i]

    def manage_funds(self, year):
        self.capital -= self.capital * self.management_fee

    def simulate(self, years, strategy):
        for year in range(years):
            self.invest(year, strategy)
            self.observe_outcomes(year)
            self.manage_funds(year)

def generate_strategy(years):
    # Create a DataFrame with allocation for each stage in each year
    # For simplicity, we evenly distribute the capital in each year across all stages
    strategy = pd.DataFrame(columns=STAGES)
    for year in range(years):
        strategy.loc[year] = [1.0 / len(STAGES)] * len(STAGES)
    return strategy

def simulate_vc(strategy):
    vc = VentureCapital(CAPITAL, MANAGEMENT_FEE)
    vc.simulate(YEARS, strategy)

    investments_df = pd.DataFrame(vc.yearly_investments, columns=['Year', 'Stage', 'Investment'])
    returns_df = pd.DataFrame(vc.yearly_returns, columns=['Year', 'Return'])

    return investments_df, returns_df

strategy = generate_strategy(YEARS)
investments_df, returns_df = simulate_vc(strategy)

investments_df
returns_df

