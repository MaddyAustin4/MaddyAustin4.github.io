# def convert_from_path(
#     pdf_path,
#     dpi=200,
#     output_folder=None,
#     first_page=None,
#     last_page=None,
#     fmt="ppm",
#     jpegopt=None,
#     thread_count=1,
#     userpw=None,
#     use_cropbox=False,
#     strict=False,
#     transparent=False,
#     single_file=False,
#     output_file=uuid_generator(),
#     poppler_path=None,
#     grayscale=False,
#     size=None,
#     paths_only=False,
#     use_pdftocairo=False,
#     timeout=None,
# ):
#     """
#         Description: Convert PDF to Image will throw whenever one of the condition is reached
#         Parameters:
#             pdf_path -> Path to the PDF that you want to convert
#             dpi -> Image quality in DPI (default 200)
#             output_folder -> Write the resulting images to a folder (instead of directly in memory)
#             first_page -> First page to process
#             last_page -> Last page to process before stopping
#             fmt -> Output image format
#             jpegopt -> jpeg options `quality`, `progressive`, and `optimize` (only for jpeg format)
#             thread_count -> How many threads we are allowed to spawn for processing
#             userpw -> PDF's password
#             use_cropbox -> Use cropbox instead of mediabox
#             strict -> When a Syntax Error is thrown, it will be raised as an Exception
#             transparent -> Output with a transparent background instead of a white one.
#             single_file -> Uses the -singlefile option from pdftoppm/pdftocairo
#             output_file -> What is the output filename or generator
#             poppler_path -> Path to look for poppler binaries
#             grayscale -> Output grayscale image(s)
#             size -> Size of the resulting image(s), uses the Pillow (width, height) standard
#             paths_only -> Don't load image(s), return paths instead (requires output_folder)
#             use_pdftocairo -> Use pdftocairo instead of pdftoppm, may help performance
#             timeout -> Raise PDFPopplerTimeoutError after the given time
#     """
#
#     if use_pdftocairo and fmt == "ppm":
#         fmt = "png"
#
#     # We make sure that if passed arguments are Path objects, they're converted to strings
#     if isinstance(pdf_path, pathlib.PurePath):
#         pdf_path = pdf_path.as_posix()
#
#     if isinstance(output_folder, pathlib.PurePath):
#         output_folder = output_folder.as_posix()
#
#     if isinstance(poppler_path, pathlib.PurePath):
#         poppler_path = poppler_path.as_posix()
#
#     page_count = pdfinfo_from_path(pdf_path, userpw, poppler_path=poppler_path)["Pages"]
#
#     # We start by getting the output format, the buffer processing function and if we need pdftocairo
#     parsed_fmt, final_extension, parse_buffer_func, use_pdfcairo_format = _parse_format(
#         fmt, grayscale
#     )
#
#     # We use pdftocairo is the format requires it OR we need a transparent output
#     use_pdfcairo = (
#         use_pdftocairo
#         or use_pdfcairo_format
#         or (transparent and parsed_fmt in TRANSPARENT_FILE_TYPES)
#     )
#
#     poppler_version_major, poppler_version_minor = _get_poppler_version(
#         "pdftocairo" if use_pdfcairo else "pdftoppm", poppler_path=poppler_path
#     )
#
#     if poppler_version_major == 0 and poppler_version_minor <= 57:
#         jpegopt = None
#
#     # If output_file isn't a generator, it will be turned into one
#     if not isinstance(output_file, types.GeneratorType) and not isinstance(
#         output_file, ThreadSafeGenerator
#     ):
#         if single_file:
#             output_file = iter([output_file])
#         else:
#             output_file = counter_generator(output_file)
#
#     if thread_count < 1:
#         thread_count = 1
#
#     if first_page is None or first_page < 1:
#         first_page = 1
#
#     if last_page is None or last_page > page_count:
#         last_page = page_count
#
#     if first_page > last_page:
#         return []
#
#     auto_temp_dir = False
#     if output_folder is None and use_pdfcairo:
#         auto_temp_dir = True
#         output_folder = tempfile.mkdtemp()
#
#     # Recalculate page count based on first and last page
#     page_count = last_page - first_page + 1
#
#     if thread_count > page_count:
#         thread_count = page_count
#
#     reminder = page_count % thread_count
#     current_page = first_page
#     processes = []
#     for _ in range(thread_count):
#         thread_output_file = next(output_file)
#
#         # Get the number of pages the thread will be processing
#         thread_page_count = page_count // thread_count + int(reminder > 0)
#         # Build the command accordingly
#         args = _build_command(
#             ["-r", str(dpi), pdf_path],
#             output_folder,
#             current_page,
#             current_page + thread_page_count - 1,
#             parsed_fmt,
#             jpegopt,
#             thread_output_file,
#             userpw,
#             use_cropbox,
#             transparent,
#             single_file,
#             grayscale,
#             size,
#         )
#
#         if use_pdfcairo:
#             args = [_get_command_path("pdftocairo", poppler_path)] + args
#         else:
#             args = [_get_command_path("pdftoppm", poppler_path)] + args
#
#         # Update page values
#         current_page = current_page + thread_page_count
#         reminder -= int(reminder > 0)
#         # Add poppler path to LD_LIBRARY_PATH
#         env = os.environ.copy()
#         if poppler_path is not None:
#             env["LD_LIBRARY_PATH"] = poppler_path + ":" + env.get("LD_LIBRARY_PATH", "")
#         # Spawn the process and save its uuid
#         processes.append(
#             (thread_output_file, Popen(args, env=env, stdout=PIPE, stderr=PIPE))
#         )
#
#     images = []
#
#     for uid, proc in processes:
#         try:
#             data, err = proc.communicate(timeout=timeout)
#         except TimeoutExpired:
#             proc.kill()
#             outs, errs = proc.communicate()
#             raise PDFPopplerTimeoutError("Run poppler poppler timeout.")
#
#         if b"Syntax Error" in err and strict:
#             raise PDFSyntaxError(err.decode("utf8", "ignore"))
#
#         if output_folder is not None:
#             images += _load_from_output_folder(
#                 output_folder, uid, final_extension, paths_only, in_memory=auto_temp_dir
#             )
#         else:
#             images += parse_buffer_func(data)
#
#     if auto_temp_dir:
#         shutil.rmtree(output_folder)
#
#     return images