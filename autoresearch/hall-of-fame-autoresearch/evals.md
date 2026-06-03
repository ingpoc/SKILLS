# Eval Suite — Hall of Fame Autoresearch

## EVAL 1: Universe Coverage

Question: Did the skill screen at least 20 symbols from the midcap_v1 universe?
Pass: At least 20 symbols screened from midcap_v1 or equivalent universe
Fail: Fewer than 20 symbols screened

## EVAL 2: v4 Filter Correctness

Question: Do reported v4-pass candidates actually pass pre90d>15, m1<20, price<2000?
Pass: Every candidate marked v4_pass has pre90d>15, m1<20, price<2000
Fail: Any v4_pass candidate fails one of the three thresholds

## EVAL 3: Outcome Verification

Question: For any candidate where T0 date has passed, did the skill verify the 90d return?
Pass: Candidates with T0 > 90 days ago have return_90d computed
Fail: Pending candidates without return_90d when T0 was more than 90 days ago

## EVAL 4: Data File Updates

Question: Did the skill update the Hall of Fame data files with new outcomes?
Pass: New WIN/NM/FP outcomes appended to feature_matrix_v2.csv or near_misses_and_fp.csv
Fail: No data file updates despite new verified outcomes

## EVAL 5: State Persistence

Question: Did the skill update state.json with iteration count and candidates_found?
Pass: state.json iteration incremented, candidates_found array updated
Fail: state.json not updated or iteration not incremented
