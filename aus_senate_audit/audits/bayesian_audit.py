# -*- coding: utf-8 -*-

""" Implements the Bayesian Audit. """

from collections import Counter
from itertools import chain
from random import gammavariate
from random import seed as set_seed
from time import time
from aus_senate_audit.audit_recorder import AuditRecorder
from aus_senate_audit.constants import RESULT_OUTPUT




def get_new_ballot_weights(election, r):
    """ Returns new ballot weights for the given election.

    The new ballot weights are constructed using Gamma Variates to draw from a Dirichlet distribution over existing
    ballots, based on existing ballot weights. The sum of the new ballot weights should be equal to :param:`r`
    (approximately). Note that ballot weights are rounded down.

    :param :class:`BaseSenateElection` election: The senate election to generate new ballot weights for.
    :param int r: The sum of the new ballot weights.

    :returns: The new ballot weights generated using Gamma Variates.
    :rtype: dict
    """
    new_ballot_weights = {}
    total = 0
    for ballot in election.get_ballots():
        weight = election.get_ballot_weight(ballot)
        new_ballot_weights[ballot] = gammavariate(weight, 1) if weight else 0
        total += new_ballot_weights[ballot]
    for ballot in election.get_ballots():
        new_ballot_weights[ballot] = int(r * new_ballot_weights[ballot] / total)
    return new_ballot_weights


def audit(election, seed, state, unpopular_freq_threshold, stage_counter=0, alpha=0.05, trials=100, quick=False):
    """ Runs a Bayesian audit on the given senate election.

    :param :class:`BaseSenateElection` election: The senate election to audit.
    :param int seed: The seed for the random number generator.
    :param float unpopular_freq_threshold: The upper bound on the frequency of trials a candidate is elected in order
        for the candidate to be deemed unpopular.
    :param int stage_counter: The current audit stage (default: 0).
    :param float alpha: The error tolerance for the given audit (default: 0.05).
    :param int trials: The number of trials performed per sample (default: 100).
    :param bool quick: A boolean indicating whether the audit should run to completion (True) or only run one stage
        (False) (default: False).
    """


    print(
        'Audit of {} election.\n'.format(election.get_type()),
        '  State: {}\n'.format(state),
        '  Election ID: {}\n'.format(election.get_election_id()),
        # '  Candidates: {}\n'.format(election.get_candidates()),
        '  Number of ballots cast: {}\n'.format(election.get_num_cast_ballots()),
        '  Number of seats being contested: {}\n'.format(election.get_num_seats()),
        '  Number of trials per sample: {}\n'.format(trials),
        '  Random number seed: {}'.format(seed),
    )
    with open(AuditRecorder(state, seed).get_file_path(RESULT_OUTPUT).format(AuditRecorder(state, seed).get_audit_dir_name()), 'a') as f:
        f.write('Audit of {} election.\n'.format(election.get_type()))
        f.write('  State: {}\n'.format(state))
        f.write('  Election ID: {}\n'.format(election.get_election_id()))
        # f.write('  Candidates: {}\n'.format(election.get_candidates()))
        f.write('  Number of ballots cast: {}\n'.format(election.get_num_cast_ballots()))
        f.write('  Number of seats being contested: {}\n'.format(election.get_num_seats()))
        f.write('  Number of trials per sample: {}\n'.format(trials))
        f.write('  Random number seed: {}\n'.format(seed))
        f.write('\n')
        f.write('\n')
        f.close()





    start_time = time()
    set_seed(seed)

    # Cast one "prior" ballot for each candidate to establish a Bayesian prior. The prior ballot is a length-one partial
    # ballot with just a first choice vote for that candidate.
    for cid in election.get_candidate_ids():
        election.add_ballot((cid,), 1)

    # Mapping from candidates to the set of ballots that elected them.
    candidate_to_ballots_map = {}
    candidate_outcomes = None

    done = False
    while True:

        stage_counter += 1
        election.draw_ballots()  # Increase sample of cast ballots.
        print(
            '\nAudit stage number: {}\n'.format(stage_counter),
            '  Sample size (including prior ballots): {}\n'.format(election.get_num_ballots_drawn()),
        )

        with open(AuditRecorder(state, seed).get_file_path(RESULT_OUTPUT).format(
                AuditRecorder(state, seed).get_audit_dir_name()), 'a') as f:
            f.write('\nAudit stage number: {}\n'.format(stage_counter))
            f.write('  Sample size (including prior ballots): {}\n'.format(election.get_num_ballots_drawn()))
            f.write('\n')
            f.close()

        # -- Run trials in a Bayesian manner --
        # Each outcome is a tuple of candidates who have been elected in lexicographical order (NOT the order in which
        # they were elected).
        print('  Performing {} Bayesian trials (posterior-based election simulations) in this stage.'.format(trials))
        with open(AuditRecorder(state, seed).get_file_path(RESULT_OUTPUT).format(
                AuditRecorder(state, seed).get_audit_dir_name()), 'a') as f:
            f.write('  Performing {} Bayesian trials (posterior-based election simulations) in this stage.\n'.format(trials))
            f.write('\n')
            f.close()

        outcomes = []
        for _ in range(trials):
            new_ballot_weights = get_new_ballot_weights(election, election.get_num_cast_ballots())
            outcome = election.get_outcome(new_ballot_weights)
            for cid in outcome:
                if cid not in candidate_to_ballots_map:
                    candidate_to_ballots_map[cid] = new_ballot_weights
            outcomes.append(outcome)

        best, freq = Counter(outcomes).most_common(1)[0]
        print(
            '  Most common outcome ({} seats):\n'.format(election.get_num_seats()),
            '  {}\n'.format(best),
            '  Frequency of most common outcome: {} / {}'.format(freq, trials),
        )

        with open(AuditRecorder(state, seed).get_file_path(RESULT_OUTPUT).format(
                AuditRecorder(state, seed).get_audit_dir_name()), 'a') as f:
            f.write('  Most common outcome ({} seats):\n'.format(election.get_num_seats()))
            f.write('  {}\n'.format(best))
            f.write('  Frequency of most common outcome: {} / {}\n'.format(freq, trials))
            f.write('\n')
            f.close()

        candidate_outcomes = Counter(chain(*outcomes))
        print(
            '  Fraction present in outcome by candidate:\n  {}'.format(
                ', '.join([
                    '{}: {}'.format(str(cid), cid_freq / trials)
                    for cid, cid_freq in sorted(candidate_outcomes.items(), key=lambda x: (x[1], x[0]))
                ]),
            ),
        )

        with open(AuditRecorder(state, seed).get_file_path(RESULT_OUTPUT).format(
                AuditRecorder(state, seed).get_audit_dir_name()), 'a') as f:
            f.write('  Fraction present in outcome by candidate:\n  {}'.format(
                ', '.join([
                    '{}: {}'.format(str(cid), cid_freq / trials)
                    for cid, cid_freq in sorted(candidate_outcomes.items(), key=lambda x: (x[1], x[0]))
                ]),
            ))
            f.write('\n')
            f.close()






        if freq >= trials * (1 - alpha):
            print(
                'Stopping because audit confirmed outcome:\n',
                '  {}\n'.format(best),
                'Total number of ballots examined: {}'.format(election.get_num_ballots_drawn()),
            )
            with open(AuditRecorder(state, seed).get_file_path(RESULT_OUTPUT).format(
                    AuditRecorder(state, seed).get_audit_dir_name()), 'a') as f:
                f.write('Stopping because audit confirmed outcome:\n')
                f.write('  {}\n'.format(best))
                f.write('Total number of ballots examined: {}'.format(election.get_num_ballots_drawn()))
                f.write('\n')
                f.close()

            done = True
            break

        if election.get_num_ballots_drawn() >= election.get_num_cast_ballots():
            print('Audit has looked at all ballots. Done.')
            with open(AuditRecorder(state, seed).get_file_path(RESULT_OUTPUT).format(
                    AuditRecorder(state, seed).get_audit_dir_name()), 'a') as f:
                f.write('Audit has looked at all ballots. Done.')
                f.close()
            done = True
            break

        if not quick:
            break

    # if candidate_outcomes is not None and done:
    #     for cid, cid_freq in sorted(candidate_outcomes.items(), key=lambda x: (x[1], x[0])):
    #         if cid_freq / trials < unpopular_freq_threshold:
    #             print(
    #                 '  One set of ballots that elected low frequency '
    #                 'candidate {} which occurred in {}% of outcomes\n'.format(str(cid), str(cid_freq)),
    #                 '  {}'.format(candidate_to_ballots_map[cid]),
    #             )
    #             with open(AuditRecorder(state, seed).get_file_path(RESULT_OUTPUT).format(
    #                     AuditRecorder(state, seed).get_audit_dir_name()), 'a') as f:
    #                 f.write('  One set of ballots that elected low frequency ')
    #                 f.write('candidate {} which occurred in {}% of outcomes\n'.format(str(cid), str(cid_freq)))
    #                 f.write('  {}'.format(candidate_to_ballots_map[cid]))
    #                 f.write('\n')
    #                 f.close()

    print('Elapsed time: {} seconds.'.format(time() - start_time))
    with open(AuditRecorder(state, seed).get_file_path(RESULT_OUTPUT).format(
            AuditRecorder(state, seed).get_audit_dir_name()), 'a') as f:
        f.write('Elapsed time: {} seconds.'.format(time() - start_time))
        f.close()
    return done
