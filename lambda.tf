data "archive_file" "python_script_file" {
  type        = "zip"
  source_file = "${path.module}/python/*"
  output_path = "${path.module}/files/lambda-function.zip"
}

resource "aws_lambda_function" "lab_lambda_image_rekognition" {
  # If the file is not in the current working directory you will need to include a 
  # path.module in the filename.
  filename      = data.archive_file.python_script_file.output_path
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_exec.arn
  handler       = "${var.lambda_function_name}.lambda_handler"

  source_code_hash = filebase64sha256(data.archive_file.python_script_file.output_path)

  runtime = "python3.11"
  timeout = 10

}