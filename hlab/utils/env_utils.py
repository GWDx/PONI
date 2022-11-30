import random
from typing import List, Type, Union

from habitat import Config, Env, make_dataset, RLEnv
from habitat_baselines.utils.env_utils import make_env_fn

from .vector_env import VectorEnv


def construct_envs(
    config: Config,
    env_class: Union[Type[Env], Type[RLEnv]],
    workers_ignore_signals: bool = False,
) -> VectorEnv:
    r"""Create VectorEnv object with specified config and env class type.
    To allow better performance, dataset are split into small ones for
    each individual env, grouped by scenes.

    :param config: configs that contain num_environments as well as information
    :param necessary to create individual environments.
    :param env_class: class type of the envs to be created.
    :param workers_ignore_signals: Passed to :ref:`habitat.VectorEnv`'s constructor

    :return: VectorEnv object created according to specification.
    """

    num_environments = config.NUM_ENVIRONMENTS
    configs = []
    env_classes = [env_class for _ in range(num_environments)]
    dataset = make_dataset(config.TASK_CONFIG.DATASET.TYPE)
    scenes = config.TASK_CONFIG.DATASET.CONTENT_SCENES
    if "*" in config.TASK_CONFIG.DATASET.CONTENT_SCENES:
        scenes = dataset.get_scenes_to_load(config.TASK_CONFIG.DATASET)

    if num_environments > 1:
        if len(scenes) == 0:
            raise RuntimeError(
                "No scenes to load, multiple process logic relies on being able to split scenes uniquely between processes"
            )

        if len(scenes) < num_environments:
            raise RuntimeError(
                "reduce the number of environments as there "
                "aren't enough number of scenes.\n"
                "num_environments: {}\tnum_scenes: {}".format(
                    num_environments, len(scenes)
                )
            )

        random.shuffle(scenes)

    scene_splits: List[List[str]] = [[] for _ in range(num_environments)]
    for idx, scene in enumerate(scenes):
        scene_splits[idx % len(scene_splits)].append(scene)

    assert sum(map(len, scene_splits)) == len(scenes)

    for i in range(num_environments):
        proc_config = config.clone()
        proc_config.defrost()

        task_config = proc_config.TASK_CONFIG
        task_config.SEED = task_config.SEED + i
        if len(scenes) > 0:
            task_config.DATASET.CONTENT_SCENES = scene_splits[i]

        task_config.SIMULATOR.HABITAT_SIM_V0.GPU_DEVICE_ID = config.SIMULATOR_GPU_ID

        task_config.SIMULATOR.AGENT_0.SENSORS = config.SENSORS

        proc_config.freeze()
        configs.append(proc_config)

    envs = VectorEnv(
        make_env_fn=make_env_fn,
        env_fn_args=tuple(zip(configs, env_classes)),
        workers_ignore_signals=workers_ignore_signals,
    )
    return envs