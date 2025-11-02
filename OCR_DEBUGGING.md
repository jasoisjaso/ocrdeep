# How to Test and Debug OCR Integration

This guide explains how to test and debug the DeepSeek-OCR integration within the worker container.

## 1. Access the Worker Container

First, get a shell inside the running `worker` container:

```bash
docker-compose exec worker bash
```

## 2. Place a Sample Image

Inside the container, you'll be in the `/app` directory. You need to have a sample image file to test with. You can copy a file from your host machine to the container:

```bash
docker cp /path/to/your/sample_image.png <container_id>:/app/sample_image.png
```

Replace `/path/to/your/sample_image.png` with the path to your image and `<container_id>` with the ID of the worker container (which you can get from `docker ps`).

## 3. Run the Test Script

Once you have a `sample_image.png` in the `/app` directory inside the container, you can run the provided test script:

```bash
python3 test_ocr.py
```

This script will:

1.  Load the DeepSeek-OCR model.
2.  Load the `absence_form.yaml` prompt.
3.  Open `sample_image.png`.
4.  Run the OCR inference.
5.  Print the raw output from the model.
6.  Attempt to parse the JSON from the output and print the result.

## 4. Debugging

- **Check the raw model output**: The script prints the full output from the model. This is useful for seeing if the model is extracting any text at all and what the format of the output is.
- **Check for JSON errors**: If the script fails to parse the JSON, the raw output will help you understand why. The model might not be returning valid JSON, or it might not be finding the fields you expect.
- **Adjust the prompt**: If the model is not extracting the correct information, you may need to adjust the `prompt_template` in `worker/prompts/absence_form.yaml`. Make the instructions as clear and specific as possible.
- **Check GPU usage**: You can monitor the GPU usage from the host machine by running `nvidia-smi` to ensure the model is running on the GPU.
