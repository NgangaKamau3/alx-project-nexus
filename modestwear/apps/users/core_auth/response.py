def standardized_response(success=True, data=None, error=None, message=None, **kwargs):
	"""
	Creates a standardized response format
	
	:success(bool, optional): Whether operation was successful. Defaults to True
	:data(dict, optional): Data to return. Defaults to None
	:error(str, optional): Error message if unsuccessful. Defaults to None
	:message(str, optional): Success or info.  Defaults to None
	**kwargs: Additional fields to include in response

	Returns:
	    dict: Formatted response dictionary.
	"""
	response = {"success": success}
	if data is not None:
		response["data"] = data
	if error is not None:
		response["error"] = error
	if message is not None:
		response["message"] = message

	for key, value in kwargs.items():
		response[key] = value
	return response