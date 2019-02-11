from ray import tune
import numpy as np

from softlearning.misc.utils import get_git_rev, deep_update

M = 256
REPARAMETERIZE = True

NUM_COUPLING_LAYERS = 2

GAUSSIAN_POLICY_PARAMS_BASE = {
    'type': 'GaussianPolicy',
    'kwargs': {
        'hidden_layer_sizes': (M, M),
        'squash': True,
    }
}

GAUSSIAN_POLICY_PARAMS_FOR_DOMAIN = {}

POLICY_PARAMS_BASE = {
    'GaussianPolicy': GAUSSIAN_POLICY_PARAMS_BASE,
}

POLICY_PARAMS_BASE.update({
    'gaussian': POLICY_PARAMS_BASE['GaussianPolicy'],
})

POLICY_PARAMS_FOR_DOMAIN = {
    'GaussianPolicy': GAUSSIAN_POLICY_PARAMS_FOR_DOMAIN,
}

POLICY_PARAMS_FOR_DOMAIN.update({
    'gaussian': POLICY_PARAMS_FOR_DOMAIN['GaussianPolicy'],
})

DEFAULT_MAX_PATH_LENGTH = 100
MAX_PATH_LENGTH_PER_DOMAIN = {
    'Point2DEnv': 50,
}

ALGORITHM_PARAMS_BASE = {
    'type': 'SAC',

    'kwargs': {
        'epoch_length': 1000,
        'train_every_n_steps': 1,
        'n_train_repeat': 1,
        'eval_render_mode': None,
        'eval_n_episodes': 1,
        'eval_deterministic': True,

        'discount': 0.99,
        'tau': 5e-3,
        'reward_scale': 1.0,
    }
}


ALGORITHM_PARAMS_ADDITIONAL = {
    'SAC': {
        'type': 'SAC',
        'kwargs': {
            'reparameterize': REPARAMETERIZE,
            'lr': 3e-4,
            'target_update_interval': 1,
            'tau': 5e-3,
            'target_entropy': 'auto',
            'store_extra_policy_info': False,
            'action_prior': 'uniform',
            'n_initial_exploration_steps': int(1e3),
        }
    },
    'SACClassifier': {
        'type': 'SACClassifier',
        'kwargs': {
            'reparameterize': REPARAMETERIZE,
            'lr': 3e-4,
            'target_update_interval': 1,
            'tau': 5e-3,
            'target_entropy': 'auto',
            'store_extra_policy_info': False,
            'action_prior': 'uniform',
            'n_initial_exploration_steps': int(1e3),
            'n_classifier_train_steps': int(1e4),
            'classifier_optim_name': 'adam'
        }
    },

    'SQL': {
        'type': 'SQL',
        'kwargs': {
            'policy_lr': 3e-4,
            'td_target_update_interval': 1,
            'n_initial_exploration_steps': int(1e3),
            'reward_scale': tune.sample_from(lambda spec: (
                {
                    'Swimmer': 30,
                    'Hopper': 30,
                    'HalfCheetah': 30,
                    'Walker': 10,
                    'Ant': 300,
                    'Humanoid': 100,
                }[spec.get('config', spec)['domain']],
            ))
        }
    }
}

DEFAULT_NUM_EPOCHS = 200

# NUM_EPOCHS_PER_DOMAIN = {
#     'Swimmer': int(3e2),
#     'Hopper': int(1e3),
#     'HalfCheetah': int(3e3),
#     'Walker': int(3e3),
#     'Ant': int(3e3),
#     'Humanoid': int(1e4),
#     'Pusher2d': int(2e3),
#     'HandManipulatePen': int(1e4),
#     'HandManipulateEgg': int(1e4),
#     'HandManipulateBlock': int(1e4),
#     'HandReach': int(1e4),
#     'Point2DEnv': int(200),
#     'Reacher': int(200),
# }

# ALGORITHM_PARAMS_PER_DOMAIN = {
#     **{
#         domain: {
#             'kwargs': {
#                 'n_epochs': NUM_EPOCHS_PER_DOMAIN.get(
#                     domain, DEFAULT_NUM_EPOCHS),
#                 'n_initial_exploration_steps': (
#                     MAX_PATH_LENGTH_PER_DOMAIN.get(
#                         domain, DEFAULT_MAX_PATH_LENGTH
#                     ) * 10),
#             }
#         } for domain in NUM_EPOCHS_PER_DOMAIN
#     }
# }

# ENV_PARAMS = {
#     'Swimmer': {  # 2 DoF
#     },
#     'Hopper': {  # 3 DoF
#     },
#     'HalfCheetah': {  # 6 DoF
#     },
#     'Walker': {  # 6 DoF
#     },
#     'Ant': {  # 8 DoF
#         'Custom': {
#             'healthy_reward': 0.0,
#             'healthy_z_range': (-np.inf, np.inf),
#             'exclude_current_positions_from_observation': False,
#         }
#     },
#     'Humanoid': {  # 17 DoF
#         'Custom': {
#             'healthy_reward': 0.0,
#             'healthy_z_range': (-np.inf, np.inf),
#             'exclude_current_positions_from_observation': False,
#         }
#     },
#     'Pusher2d': {  # 3 DoF
#         'Default': {
#             'arm_object_distance_cost_coeff': 0.0,
#             'goal_object_distance_cost_coeff': 1.0,
#             'goal': (0, -1),
#         },
#         'DefaultReach': {
#             'arm_goal_distance_cost_coeff': 1.0,
#             'arm_object_distance_cost_coeff': 0.0,
#         },
#         'ImageDefault': {
#             'image_shape': (32, 32, 3),
#             'arm_object_distance_cost_coeff': 0.0,
#             'goal_object_distance_cost_coeff': 3.0,
#         },
#         'ImageReach': {
#             'image_shape': (32, 32, 3),
#             'arm_goal_distance_cost_coeff': 1.0,
#             'arm_object_distance_cost_coeff': 0.0,
#         },
#         'BlindReach': {
#             'image_shape': (32, 32, 3),
#             'arm_goal_distance_cost_coeff': 1.0,
#             'arm_object_distance_cost_coeff': 0.0,
#         }
#     },
#     'Point2DEnv': {
#         'Default': {
#             'observation_keys': ('observation', ),
#         },
#         'Wall': {
#             'observation_keys': ('observation', ),
#         },
#     }
# }

NUM_CHECKPOINTS = 10


def get_variant_spec_base(universe, domain, task, policy, algorithm):
    # algorithm_params = deep_update(
    #     ALGORITHM_PARAMS_BASE,
    #     ALGORITHM_PARAMS_PER_DOMAIN.get(domain, {})
    # )
    # algorithm_params = deep_update(
    #     algorithm_params,
    #     ALGORITHM_PARAMS_ADDITIONAL.get(algorithm, {})
    # )
    algorithm_params = ALGORITHM_PARAMS_BASE
    algorithm_params = deep_update(
            algorithm_params,
            ALGORITHM_PARAMS_ADDITIONAL.get(algorithm, {})
        )

    variant_spec = {
        'domain': domain,
        'task': task,
        'universe': universe,
        'git_sha': get_git_rev(),

        #'env_params': ENV_PARAMS.get(domain, {}).get(task, {}),
        'policy_params': deep_update(
            POLICY_PARAMS_BASE[policy],
            POLICY_PARAMS_FOR_DOMAIN[policy].get(domain, {})
        ),
        'Q_params': {
            'type': 'double_feedforward_Q_function',
            'kwargs': {
                'hidden_layer_sizes': (M, M),
            }
        },
        'algorithm_params': algorithm_params,
        'replay_pool_params': {
            'type': 'SimpleReplayPool',
            'kwargs': {
                'max_size': 1e6,
            }
        },
        'sampler_params': {
            'type': 'SimpleSampler',
            'kwargs': {
                'max_path_length': MAX_PATH_LENGTH_PER_DOMAIN.get(
                    domain, DEFAULT_MAX_PATH_LENGTH),
                'min_pool_size': MAX_PATH_LENGTH_PER_DOMAIN.get(
                    domain, DEFAULT_MAX_PATH_LENGTH),
                'batch_size': 256,
            }
        },
        'run_params': {
            'seed': tune.sample_from(
                lambda spec: np.random.randint(0, 10000)),
            'checkpoint_at_end': True,
            'checkpoint_frequency':  DEFAULT_NUM_EPOCHS // NUM_CHECKPOINTS,
            'checkpoint_replay_pool': False,
        },
    }

    return variant_spec


def get_variant_spec_classifier(universe,
                                domain,
                                task,
                                policy,
                                algorithm,
                                *args,
                                **kwargs):
    variant_spec = get_variant_spec_base(
        universe, domain, task, policy, algorithm, *args, **kwargs)
    
    classifier_layer_size = L = 256
    variant_spec['classifier_params'] = {
            'type': 'feedforward_classifier',
            'kwargs': {
                'hidden_layer_sizes': (L,L),
            }
        }

    return variant_spec

# def get_variant_spec_image(universe,
#                            domain,
#                            task,
#                            policy,
#                            algorithm,
#                            *args,
#                            **kwargs):
#     variant_spec = get_variant_spec_base(
#         universe, domain, task, policy, algorithm, *args, **kwargs)

#     if 'image' in task.lower() or 'image' in domain.lower():
#         preprocessor_params = {
#             'type': 'convnet_preprocessor',
#             'kwargs': {
#                 'image_shape': variant_spec['env_params']['image_shape'],
#                 'output_size': M,
#                 'conv_filters': (4, 4),
#                 'conv_kernel_sizes': ((3, 3), (3, 3)),
#                 'pool_type': 'MaxPool2D',
#                 'pool_sizes': ((2, 2), (2, 2)),
#                 'pool_strides': (2, 2),
#                 'dense_hidden_layer_sizes': (),
#             },
#         }
#         variant_spec['policy_params']['kwargs']['preprocessor_params'] = (
#             preprocessor_params.copy())
#         variant_spec['Q_params']['kwargs']['preprocessor_params'] = (
#             preprocessor_params.copy())

#     return variant_spec


def get_variant_spec(args):
    universe, domain, task, algorithm = args.universe, args.domain, args.task, args.algorithm

    # if ('image' in task.lower()
    #     or 'blind' in task.lower()
    #     or 'image' in domain.lower()):
    #     variant_spec = get_variant_spec_image(
    #         universe, domain, task, args.policy, args.algorithm)
    # else:
    if args.algorithm in ['SACClassifier']:
        variant_spec = get_variant_spec_classifier(
            universe, domain, task, args.policy, args.algorithm)
    else:
        variant_spec = get_variant_spec_base(
            universe, domain, task, args.policy, args.algorithm)

    if args.checkpoint_replay_pool is not None:
        variant_spec['run_params']['checkpoint_replay_pool'] = (
            args.checkpoint_replay_pool)

    return variant_spec
