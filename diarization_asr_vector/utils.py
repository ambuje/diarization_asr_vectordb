# Define the speakers and their speaking intervals
# intervals = [
#     ("SPEAKER_00", 0.008, 59.889),
#     ("SPEAKER_01", 16.646, 17.495),
#     ("SPEAKER_01", 17.699, 18.208),
#     ("SPEAKER_01", 35.237, 35.696),
#     ("SPEAKER_01", 50.042, 50.653),
#     ("SPEAKER_00", 60.415, 147.376)
# ]
def split_overlap(intervals):
    r=[]
# Sort the intervals by start time
    intervals.sort(key=lambda x: x[1])

    # Initialize the result
    result = []

    # Iterate over the intervals
    for speaker, start, end in intervals:
        # If the result is not empty and the current interval overlaps with the last interval in the result
        if result and start < result[-1][2]:
            # Split the last interval in the result
            last_speaker, last_start, last_end = result.pop()
            result.append((last_speaker, last_start, start))
            result.append((speaker, start, min(end, last_end)))
            if end < last_end:
                result.append((last_speaker, end, last_end))
        else:
            # Add the current interval to the result
            result.append((speaker, start, end))

    # Print the result
    for speaker, start, end in result:
        r.append((speaker,start,end))
        # print(f"{speaker} {start}--{end}")
    return r

# Define the speakers and their speaking intervals
# intervals = [
#     ("SPEAKER_00", 0.008, 59.889),
#     ("SPEAKER_01", 16.646, 17.495),
#     ("SPEAKER_01", 17.699, 18.208),
#     ("SPEAKER_01", 35.237, 35.696),
#     ("SPEAKER_01", 50.042, 50.653),
#     ("SPEAKER_00", 60.415, 287.665)
# ]
def combine_timestamp(intervals):
    r=[]
# Sort the intervals by start time
    intervals.sort(key=lambda x: x[1])

    # Initialize the result
    result = []

    # Iterate over the intervals
    for speaker, start, end in intervals:
        # If the result is not empty and the current interval overlaps with the last interval in the result
        if result and start - result[-1][2] < 1000 and speaker == result[-1][0]:
            # Merge the current interval with the last interval in the result
            last_speaker, last_start, last_end = result.pop()
            result.append((last_speaker, last_start, max(end, last_end)))
        else:
            # Add the current interval to the result
            result.append((speaker, start, end))

    # Print the result
    for speaker, start, end in result:
        r.append((speaker,start,end))
        # print(f"{speaker} {start}--{end}")
    return r

def millisec(timeStr):
  spl = timeStr.split(":")
  s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
  return s

import re
def group_():
  dzs = open('diarization.txt').read().splitlines()

  groups = []
  g = []
  lastend = 0

  for d in dzs:   
    if g and (g[0].split()[-1] != d.split()[-1]):      #same speaker
      groups.append(g)
      g = []
    
    g.append(d)
    
    end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
    end = millisec(end)
    if (lastend > end):       #segment engulfed by a previous segment
      groups.append(g)
      g = [] 
    else:
      lastend = end
  if g:
    groups.append(g)
    return groups

def break_string_near_k_words(input_string,string_break):
    words = input_string.split()
    output_strings = []
    current_string = ""

    word_count = 0
    for word in words:
        word_count += 1
        current_string += word + " "

        if word_count >= string_break and word.endswith("."):
            output_strings.append(current_string.strip())
            current_string = ""
            word_count = 0
        elif word_count >= string_break:
            last_period_index = current_string.rfind(".")
            if last_period_index != -1:
                output_strings.append(current_string[:last_period_index + 1].strip())
                current_string = current_string[last_period_index + 1:].strip()
                word_count = len(current_string.split())

    # Append the remaining words if any
    if current_string.strip():
        output_strings.append(current_string.strip())

    return output_strings
