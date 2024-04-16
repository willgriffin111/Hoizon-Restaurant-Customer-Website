import replicate

input = {
    "image": "https://replicate.delivery/pbxt/KW7Getr2zD5ECxySdBZtLmPa322lNkXrpkMdKcmxeaDmq2b1/MTk4MTczMTkzNzI1Mjg5NjYy.webp",
    "style": "Clay",
    "prompt": "a person in a post apocalyptic war game",
    "instant_id_strength": 0.8
}

output = replicate.run(
    "fofr/face-to-many:35cea9c3164d9fb7fbd48b51503eabdb39c9d04fdaef9a68f368bed8087ec5f9",
    input=input
)
print(output)
#=> ["https://replicate.delivery/pbxt/R1ayGe5efoQbaoRzgDEJdLs...