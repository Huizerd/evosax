import jax
import chex
from typing import Tuple
from functools import partial
from .cma_es import CMA_ES
from ..restarts import IPOP_Restarter
from ..restarts.termination import cma_criterion


class IPOP_CMA_ES(object):
    def __init__(self, num_dims: int, popsize: int, elite_ratio: float = 0.5):
        """IPOP-CMA-ES (Auer & Hansen, 2005).
        Reference: http://www.cmap.polytechnique.fr/~nikolaus.hansen/cec2005ipopcmaes.pdf
        """
        self.strategy_name = "IPOP_CMA_ES"
        # Instantiate base strategy & wrap it with restart wrapper
        self.strategy = CMA_ES(
            num_dims=num_dims, popsize=popsize, elite_ratio=elite_ratio
        )
        self.wrapped_strategy = IPOP_Restarter(
            self.strategy, stop_critera=[cma_criterion]
        )

    @property
    def default_params(self) -> chex.ArrayTree:
        """Return default parameters of evolution strategy."""
        return self.wrapped_strategy.default_params

    @partial(jax.jit, static_argnums=(0,))
    def initialize(
        self, rng: chex.PRNGKey, params: chex.ArrayTree
    ) -> chex.ArrayTree:
        """`initialize` the evolution strategy."""
        return self.wrapped_strategy.initialize(rng, params)

    def ask(
        self, rng: chex.PRNGKey, state: chex.ArrayTree, params: chex.ArrayTree
    ) -> Tuple[chex.Array, chex.ArrayTree]:
        """`ask` for new parameter candidates to evaluate next."""
        return self.wrapped_strategy.ask(rng, state, params)

    @partial(jax.jit, static_argnums=(0,))
    def tell(
        self,
        x: chex.Array,
        fitness: chex.Array,
        state: chex.ArrayTree,
        params: chex.ArrayTree,
    ) -> chex.ArrayTree:
        """`tell` performance data for strategy state update."""
        return self.wrapped_strategy.tell(x, fitness, state, params)