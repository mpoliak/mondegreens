def get_stimuli_wnp1():
    """
    Code from the experiment run on 04/26/2023. 
    It was buggy in that Finnish and English stimuli
    had different noise levels (English was -12, -6, 3. 9,
    while Finnish was -9, -3, 6, 12)
    """
    experimental_list = []
    for item in range(ITEMS):
        language = LANGUAGES[item % 2]
        if item < ITEMS / 2:
            prime = PRIME[0]
        else:
            prime = PRIME[1]
        noise_level = NOISE_LEVELS[item % len(NOISE_LEVELS)]
        experimental_list.append(
                {"item":item+1,
                "language":language,
                "prime":prime,
                "prime_id":-1,
                "noise_level":noise_level}
            )
    ## Randomize pairings with sentences
    item_order = list(range(ITEMS))
    random.shuffle(item_order)
    for i in range(len(experimental_list)):
        experimental_list[i]["item"] = item_order[i]+1
    random.shuffle(experimental_list)

    for i in range(len(experimental_list)):
        experimental_list[i]["presentation_order"] = i+1


    different_primes_en = [i for i in range(CONDITIONS*2)]
    random.shuffle(different_primes_en)
    different_primes_fi = [i for i in range(CONDITIONS*2)]
    random.shuffle(different_primes_en)
    different_primes = {
            "en":different_primes_en,
            "fi":different_primes_fi
            }

    for item in experimental_list:
        if item["prime"] == "same":
            prime_link = f"primes/{item['language']}_{item['item']}_prime_same.mp3"
        else:
            different_prime_id = different_primes[item["language"]].pop()
            prime_link = f"primes/{item['language']}_{different_prime_id+1}_prime_different.mp3"
        
        experimental_list[item["presentation_order"]-1]["prime_link"] = GITHUB_PREFIX + prime_link + GITHUB_SUFFIX
        critical_link = f"noise_{item['noise_level']}/{item['language']}_{item['item']}_noise_{item['noise_level']}.mp3"
        experimental_list[item["presentation_order"]-1]["critical_link"] = GITHUB_PREFIX + critical_link + GITHUB_SUFFIX
        if item["prime"] != "same":
            experimental_list[item["presentation_order"]-1]["prime_id"] = different_prime_id

