# MinhOS System Truth Report
Generated: 2025-07-24T11:35:32.051193
Working Directory: /home/colindo/Sync/minh_v3

## Executive Summary

- Total Files: 6251
- Service Files: 20
- Services Running: 2/9
- Config Files: 3
- Recent Errors: 0

## Service Health

| Service | Port | Status |
|---------|------|--------|
| ai_brain | 9006 | [DOWN] {'status': 'down (connection refused)', 'response_time_ms': None, 'status_code': None, 'error': 'Connection refused', 'last_checked': '2025-07-24T11:36:13.771662'} |
| live_integration | 9005 | [DOWN] {'status': 'down (connection refused)', 'response_time_ms': None, 'status_code': None, 'error': 'Connection refused', 'last_checked': '2025-07-24T11:36:13.771526'} |
| minhos_api | 8888 | [UP] {'status': 'running (socket check)', 'response_time_ms': 0.052928924560546875, 'status_code': None, 'error': None, 'last_checked': '2025-07-24T11:36:13.771470'} |
| minhos_dashboard | 8888 | [UP] {'status': 'running (socket check)', 'response_time_ms': 0.06341934204101562, 'status_code': None, 'error': None, 'last_checked': '2025-07-24T11:36:13.771403'} |
| multi_chart | 9004 | [DOWN] {'status': 'down (connection refused)', 'response_time_ms': None, 'status_code': None, 'error': 'Connection refused', 'last_checked': '2025-07-24T11:36:13.771619'} |
| sierra_bridge | 8765 | [DOWN] {'status': 'down (connection refused)', 'response_time_ms': None, 'status_code': None, 'error': 'Connection refused', 'last_checked': '2025-07-24T11:36:13.771220'} |
| sierra_bridge_market | 8765 | [DOWN] {'status': 'down (connection refused)', 'response_time_ms': None, 'status_code': None, 'error': 'Connection refused', 'last_checked': '2025-07-24T11:36:13.771350'} |
| sierra_client | 9003 | [DOWN] {'status': 'down (connection refused)', 'response_time_ms': None, 'status_code': None, 'error': 'Connection refused', 'last_checked': '2025-07-24T11:36:13.771574'} |
| trading_engine | 9007 | [DOWN] {'status': 'down (connection refused)', 'response_time_ms': None, 'status_code': None, 'error': 'Connection refused', 'last_checked': '2025-07-24T11:36:13.771704'} |

## File Structure

```
./
  [LIB] client.py - 129 lines (ports: 8765)
  [CONFIG] config.py - 37 lines (ports: 8765)
  [LAUNCH] minh.py - 417 lines (ports: 8765)
  [LIB] trading_client.py - 144 lines (ports: 8765)
User Tools/
  [LIB] add_documentation.py - 727 lines
  [LIB] context_for_ai.py - 1971 lines (ports: 2000,8000,8765,8888,9002)
  [LIB] production_readiness.py - 981 lines
  [EXEC] system_truth.py - 1185 lines (ports: 8000,8765,8888,9003,9004,9005,9006,9007)
bridge_windows/
  [LIB] file_access_api.py - 238 lines
examples/
  [LIB] unified_market_data_usage.py - 120 lines
minhos/
  [LIB] __init__.py - 32 lines
  [LIB] main.py - 147 lines
minhos/core/
  [LIB] __init__.py - 13 lines
  [SVC] base_service.py - 398 lines
  [CONFIG] config.py - 389 lines (ports: 6379,11434)
  [LIB] decision_quality.py - 622 lines
  [LIB] market_data_adapter.py - 168 lines
  [LIB] market_data_store.py - 458 lines
  [LIB] nlp_provider.py - 266 lines
minhos/core/providers/
  [LIB] __init__.py - 1 lines
  [LIB] kimi_k2_provider.py - 292 lines
  [LIB] local_llm_provider.py - 249 lines (ports: 11434)
minhos/dashboard/
  [LIB] __init__.py - 10 lines
  [LIB] api.py - 994 lines
  [LIB] main.py - 351 lines (ports: 8888)
  [LIB] websocket_chat.py - 149 lines
minhos/models/
  [LIB] __init__.py - 16 lines
  [LIB] market.py - 197 lines
minhos/services/
  [LIB] __init__.py - 122 lines
  [SVC] ai_brain_service.py - 746 lines
  [SVC] chat_service.py - 448 lines
  [LIB] live_trading_integration.py - 646 lines (ports: 8888)
  [LIB] market_data.py - 610 lines
  [LIB] market_data_migrated.py - 364 lines
  [LIB] multi_chart_collector.py - 476 lines
  [LIB] orchestrator.py - 384 lines (ports: 8888)
  [LIB] pattern_analyzer.py - 1045 lines
  [LIB] risk_manager.py - 1108 lines
  [LIB] sierra_client.py - 670 lines
  [LIB] sierra_historical_data.py - 405 lines (ports: 8765)
  [LIB] state_manager.py - 1000 lines (ports: 9002)
  [LIB] trading_engine.py - 1203 lines
  [LIB] web_api.py - 731 lines
scripts/
  [LIB] diagnose_streaming.py - 266 lines (ports: 8765)
  [LIB] historical_data_manager.py - 181 lines
src/services/
  [LIB] sierra_client_optimized.py - 214 lines (ports: 8765)
  [LIB] sierra_client_sse.py - 227 lines (ports: 8765)
ta-lib/venv/lib/python3.10/site-packages/
  [LIB] six.py - 1003 lines
  [LIB] typing_extensions.py - 4244 lines
ta-lib/venv/lib/python3.10/site-packages/_distutils_hack/
  [LIB] __init__.py - 132 lines
  [LIB] override.py - 1 lines
ta-lib/venv/lib/python3.10/site-packages/_yaml/
  [LIB] __init__.py - 33 lines
ta-lib/venv/lib/python3.10/site-packages/aiofiles/
  [LIB] __init__.py - 22 lines
  [LIB] base.py - 69 lines
  [LIB] os.py - 58 lines
  [LIB] ospath.py - 30 lines
ta-lib/venv/lib/python3.10/site-packages/aiofiles/tempfile/
  [LIB] __init__.py - 357 lines
  [LIB] temptypes.py - 69 lines
ta-lib/venv/lib/python3.10/site-packages/aiofiles/threadpool/
  [LIB] __init__.py - 139 lines
  [LIB] binary.py - 104 lines
  [LIB] text.py - 64 lines
  [LIB] utils.py - 72 lines
ta-lib/venv/lib/python3.10/site-packages/aiohappyeyeballs/
  [LIB] __init__.py - 14 lines
  [LIB] _staggered.py - 207 lines
  [LIB] impl.py - 259 lines
  [LIB] types.py - 17 lines
  [LIB] utils.py - 97 lines
ta-lib/venv/lib/python3.10/site-packages/aiohttp/
  [LIB] __init__.py - 278 lines
  [LIB] _cookie_helpers.py - 309 lines
  [LIB] abc.py - 268 lines
  [LIB] base_protocol.py - 100 lines
  [LIB] client.py - 1613 lines
  [LIB] client_exceptions.py - 421 lines
  [LIB] client_middleware_digest_auth.py - 474 lines
  [LIB] client_middlewares.py - 55 lines
  [LIB] client_proto.py - 359 lines
  [LIB] client_reqrep.py - 1533 lines
  [LIB] client_ws.py - 428 lines
  [LIB] compression_utils.py - 278 lines
  [LIB] connector.py - 1834 lines
  [LIB] cookiejar.py - 522 lines
  [LIB] formdata.py - 179 lines
  [LIB] hdrs.py - 121 lines
  [LIB] helpers.py - 958 lines
  [LIB] http.py - 72 lines
  [LIB] http_exceptions.py - 112 lines
  [LIB] http_parser.py - 1050 lines
  [LIB] http_websocket.py - 36 lines
  [LIB] http_writer.py - 378 lines
  [LIB] log.py - 8 lines
  [LIB] multipart.py - 1140 lines
  [LIB] payload.py - 1124 lines
  [LIB] payload_streamer.py - 78 lines
  [TEST] pytest_plugin.py - 444 lines
  [LIB] resolver.py - 274 lines
  [LIB] streams.py - 727 lines
  [LIB] tcp_helpers.py - 37 lines
  [LIB] tracing.py - 455 lines
  [LIB] typedefs.py - 69 lines
  [LIB] web.py - 605 lines
  [LIB] web_app.py - 620 lines
  [LIB] web_exceptions.py - 452 lines
  [LIB] web_fileresponse.py - 418 lines
  [LIB] web_log.py - 216 lines
  [LIB] web_middlewares.py - 121 lines
  [LIB] web_protocol.py - 792 lines
  [LIB] web_request.py - 916 lines (ports: 8080)
  [LIB] web_response.py - 856 lines
  [LIB] web_routedef.py - 214 lines
  [LIB] web_runner.py - 399 lines (ports: 8443)
  [SVC] web_server.py - 84 lines
  [LIB] web_urldispatcher.py - 1303 lines
  [LIB] web_ws.py - 631 lines
  [LIB] worker.py - 255 lines
ta-lib/venv/lib/python3.10/site-packages/aiohttp/_websocket/
  [LIB] __init__.py - 1 lines
  [LIB] helpers.py - 147 lines
  [LIB] models.py - 84 lines
  [LIB] reader.py - 31 lines
  [LIB] reader_c.py - 476 lines
  [LIB] reader_py.py - 476 lines
  [LIB] writer.py - 178 lines
ta-lib/venv/lib/python3.10/site-packages/aiosignal/
  [LIB] __init__.py - 59 lines
ta-lib/venv/lib/python3.10/site-packages/annotated_types/
  [LIB] __init__.py - 432 lines
ta-lib/venv/lib/python3.10/site-packages/anyio/
  [LIB] __init__.py - 85 lines
  [LIB] from_thread.py - 527 lines
  [LIB] lowlevel.py - 161 lines
  [TEST] pytest_plugin.py - 272 lines
  [LIB] to_interpreter.py - 218 lines
  [LIB] to_process.py - 258 lines
  [LIB] to_thread.py - 69 lines
ta-lib/venv/lib/python3.10/site-packages/anyio/_backends/
  [LIB] __init__.py - 0 lines
  [LIB] _asyncio.py - 2816 lines
  [LIB] _trio.py - 1334 lines
ta-lib/venv/lib/python3.10/site-packages/anyio/_core/
  [LIB] __init__.py - 0 lines
  [LIB] _asyncio_selector_thread.py - 167 lines
  [LIB] _eventloop.py - 166 lines
  [LIB] _exceptions.py - 126 lines
  [LIB] _fileio.py - 742 lines
  [LIB] _resources.py - 18 lines
  [LIB] _signals.py - 27 lines
  [LIB] _sockets.py - 792 lines
  [LIB] _streams.py - 52 lines
  [LIB] _subprocesses.py - 202 lines
  [LIB] _synchronization.py - 732 lines
  [LIB] _tasks.py - 158 lines
  [LIB] _tempfile.py - 616 lines
  [TEST] _testing.py - 78 lines
  [LIB] _typedattr.py - 81 lines
ta-lib/venv/lib/python3.10/site-packages/anyio/abc/
  [LIB] __init__.py - 55 lines
  [LIB] _eventloop.py - 376 lines
  [LIB] _resources.py - 33 lines
  [LIB] _sockets.py - 194 lines
  [LIB] _streams.py - 203 lines
  [LIB] _subprocesses.py - 79 lines
  [LIB] _tasks.py - 101 lines
  [TEST] _testing.py - 65 lines
ta-lib/venv/lib/python3.10/site-packages/anyio/streams/
  [LIB] __init__.py - 0 lines
  [LIB] buffered.py - 119 lines
  [LIB] file.py - 148 lines
  [LIB] memory.py - 317 lines
  [LIB] stapled.py - 141 lines
  [LIB] text.py - 147 lines
  [LIB] tls.py - 352 lines
ta-lib/venv/lib/python3.10/site-packages/async_timeout/
  [LIB] __init__.py - 276 lines
ta-lib/venv/lib/python3.10/site-packages/attr/
  [LIB] __init__.py - 104 lines
  [LIB] _cmp.py - 160 lines
  [LIB] _compat.py - 94 lines
  [CONFIG] _config.py - 31 lines
  [LIB] _funcs.py - 468 lines
  [LIB] _make.py - 3123 lines
  [LIB] _next_gen.py - 623 lines
  [LIB] _version_info.py - 86 lines
  [LIB] converters.py - 162 lines
  [LIB] exceptions.py - 95 lines
  [LIB] filters.py - 72 lines
  [LIB] setters.py - 79 lines
  [LIB] validators.py - 710 lines
ta-lib/venv/lib/python3.10/site-packages/attrs/
  [LIB] __init__.py - 69 lines
  [LIB] converters.py - 3 lines
  [LIB] exceptions.py - 3 lines
  [LIB] filters.py - 3 lines
  [LIB] setters.py - 3 lines
  [LIB] validators.py - 3 lines
ta-lib/venv/lib/python3.10/site-packages/click/
  [LIB] __init__.py - 123 lines
  [LIB] _compat.py - 622 lines
  [LIB] _termui_impl.py - 839 lines
  [LIB] _textwrap.py - 51 lines
  [LIB] _winconsole.py - 296 lines
  [LIB] core.py - 3135 lines
  [LIB] decorators.py - 551 lines
  [LIB] exceptions.py - 308 lines
  [LIB] formatting.py - 301 lines
  [LIB] globals.py - 67 lines
  [LIB] parser.py - 532 lines
  [LIB] shell_completion.py - 644 lines
  [LIB] termui.py - 877 lines
  [TEST] testing.py - 565 lines
  [LIB] types.py - 1165 lines
  [LIB] utils.py - 627 lines
ta-lib/venv/lib/python3.10/site-packages/dateutil/
  [LIB] __init__.py - 24 lines
  [LIB] _common.py - 43 lines
  [LIB] _version.py - 4 lines
  [LIB] easter.py - 89 lines
  [LIB] relativedelta.py - 599 lines
  [LIB] rrule.py - 1737 lines
  [LIB] tzwin.py - 2 lines
  [LIB] utils.py - 71 lines
ta-lib/venv/lib/python3.10/site-packages/dateutil/parser/
  [LIB] __init__.py - 61 lines
  [LIB] _parser.py - 1613 lines
  [LIB] isoparser.py - 416 lines
ta-lib/venv/lib/python3.10/site-packages/dateutil/tz/
  [LIB] __init__.py - 12 lines
  [LIB] _common.py - 419 lines
  [LIB] _factories.py - 80 lines
  [LIB] tz.py - 1849 lines
  [LIB] win.py - 370 lines
ta-lib/venv/lib/python3.10/site-packages/dateutil/zoneinfo/
  [LIB] __init__.py - 167 lines
  [LIB] rebuild.py - 75 lines
ta-lib/venv/lib/python3.10/site-packages/exceptiongroup/
  [LIB] __init__.py - 46 lines
  [LIB] _catch.py - 138 lines
  [LIB] _exceptions.py - 336 lines
  [LIB] _formatting.py - 601 lines
  [LIB] _suppress.py - 55 lines
  [LIB] _version.py - 21 lines
ta-lib/venv/lib/python3.10/site-packages/fastapi/
  [LIB] __init__.py - 25 lines
  [LIB] __main__.py - 3 lines
  [LIB] _compat.py - 664 lines
  [LIB] applications.py - 4588 lines
  [LIB] background.py - 59 lines
  [LIB] cli.py - 13 lines
  [LIB] concurrency.py - 39 lines
  [LIB] datastructures.py - 204 lines
  [LIB] encoders.py - 343 lines
  [LIB] exception_handlers.py - 34 lines
  [LIB] exceptions.py - 176 lines
  [LIB] logger.py - 3 lines
  [LIB] param_functions.py - 2360 lines
  [LIB] params.py - 786 lines
  [LIB] requests.py - 2 lines
  [LIB] responses.py - 48 lines
  [LIB] routing.py - 4440 lines
  [LIB] staticfiles.py - 1 lines
  [LIB] templating.py - 1 lines
  [TEST] testclient.py - 1 lines
  [LIB] types.py - 10 lines
  [LIB] utils.py - 220 lines
  [LIB] websockets.py - 3 lines
ta-lib/venv/lib/python3.10/site-packages/fastapi/dependencies/
  [LIB] __init__.py - 0 lines
  [LIB] models.py - 37 lines
  [LIB] utils.py - 1001 lines
ta-lib/venv/lib/python3.10/site-packages/fastapi/middleware/
  [LIB] __init__.py - 1 lines
  [LIB] cors.py - 1 lines
  [LIB] gzip.py - 1 lines
  [LIB] httpsredirect.py - 3 lines
  [LIB] trustedhost.py - 3 lines
  [LIB] wsgi.py - 1 lines
ta-lib/venv/lib/python3.10/site-packages/fastapi/openapi/
  [LIB] __init__.py - 0 lines
  [LIB] constants.py - 3 lines
  [LIB] docs.py - 344 lines
  [LIB] models.py - 445 lines
  [LIB] utils.py - 569 lines
ta-lib/venv/lib/python3.10/site-packages/fastapi/security/
  [LIB] __init__.py - 15 lines
  [LIB] api_key.py - 288 lines
  [LIB] base.py - 6 lines
  [LIB] http.py - 423 lines
  [LIB] oauth2.py - 653 lines
  [LIB] open_id_connect_url.py - 84 lines
  [LIB] utils.py - 10 lines
ta-lib/venv/lib/python3.10/site-packages/frozenlist/
  [LIB] __init__.py - 86 lines
ta-lib/venv/lib/python3.10/site-packages/h11/
  [LIB] __init__.py - 62 lines
  [LIB] _abnf.py - 132 lines
  [LIB] _connection.py - 659 lines
  [LIB] _events.py - 369 lines
  [LIB] _headers.py - 282 lines
  [LIB] _readers.py - 250 lines
  [LIB] _receivebuffer.py - 153 lines
  [LIB] _state.py - 365 lines
  [LIB] _util.py - 135 lines
  [LIB] _version.py - 16 lines
  [LIB] _writers.py - 145 lines
ta-lib/venv/lib/python3.10/site-packages/idna/
  [LIB] __init__.py - 45 lines
  [LIB] codec.py - 122 lines
  [LIB] compat.py - 15 lines
  [LIB] core.py - 437 lines
  [LIB] idnadata.py - 4243 lines
  [LIB] intranges.py - 57 lines
  [LIB] package_data.py - 1 lines
  [LIB] uts46data.py - 8681 lines
ta-lib/venv/lib/python3.10/site-packages/markdown_it/
  [LIB] __init__.py - 5 lines
  [LIB] _compat.py - 11 lines
  [LIB] _punycode.py - 67 lines
  [LIB] main.py - 355 lines
  [LIB] parser_block.py - 111 lines
  [LIB] parser_core.py - 45 lines
  [LIB] parser_inline.py - 147 lines
  [LIB] renderer.py - 336 lines
  [LIB] ruler.py - 276 lines
  [LIB] token.py - 180 lines
  [LIB] tree.py - 345 lines
  [LIB] utils.py - 176 lines
ta-lib/venv/lib/python3.10/site-packages/markdown_it/cli/
  [LIB] __init__.py - 0 lines
  [LIB] parse.py - 109 lines
ta-lib/venv/lib/python3.10/site-packages/markdown_it/common/
  [LIB] __init__.py - 0 lines
  [LIB] entities.py - 4 lines
  [LIB] html_blocks.py - 68 lines
  [LIB] html_re.py - 40 lines
  [LIB] normalize_url.py - 81 lines
  [LIB] utils.py - 318 lines
ta-lib/venv/lib/python3.10/site-packages/markdown_it/helpers/
  [LIB] __init__.py - 6 lines
  [LIB] parse_link_destination.py - 86 lines
  [LIB] parse_link_label.py - 43 lines
  [LIB] parse_link_title.py - 60 lines
ta-lib/venv/lib/python3.10/site-packages/markdown_it/presets/
  [LIB] __init__.py - 28 lines
  [LIB] commonmark.py - 74 lines
  [LIB] default.py - 35 lines
  [LIB] zero.py - 43 lines
ta-lib/venv/lib/python3.10/site-packages/markdown_it/rules_block/
  [LIB] __init__.py - 27 lines
  [LIB] blockquote.py - 299 lines
  [LIB] code.py - 35 lines
  [LIB] fence.py - 101 lines
  [LIB] heading.py - 68 lines
  [LIB] hr.py - 55 lines
  [LIB] html_block.py - 90 lines
  [LIB] lheading.py - 86 lines
  [LIB] list.py - 345 lines
  [LIB] paragraph.py - 65 lines
  [LIB] reference.py - 215 lines
  [LIB] state_block.py - 261 lines
  [LIB] table.py - 236 lines
ta-lib/venv/lib/python3.10/site-packages/markdown_it/rules_core/
  [LIB] __init__.py - 19 lines
  [LIB] block.py - 13 lines
  [LIB] inline.py - 10 lines
  [LIB] linkify.py - 149 lines
  [LIB] normalize.py - 18 lines
  [LIB] replacements.py - 126 lines
  [LIB] smartquotes.py - 202 lines
  [LIB] state_core.py - 25 lines
  [LIB] text_join.py - 34 lines
ta-lib/venv/lib/python3.10/site-packages/markdown_it/rules_inline/
  [LIB] __init__.py - 31 lines
  [LIB] autolink.py - 77 lines
  [LIB] backticks.py - 72 lines
  [LIB] balance_pairs.py - 137 lines
  [LIB] emphasis.py - 102 lines
  [LIB] entity.py - 53 lines
  [LIB] escape.py - 92 lines
  [LIB] fragments_join.py - 43 lines
  [LIB] html_inline.py - 43 lines
  [LIB] image.py - 148 lines
  [LIB] link.py - 151 lines
  [LIB] linkify.py - 61 lines
  [LIB] newline.py - 43 lines
  [LIB] state_inline.py - 166 lines
  [LIB] strikethrough.py - 127 lines
  [LIB] text.py - 53 lines
ta-lib/venv/lib/python3.10/site-packages/mdurl/
  [LIB] __init__.py - 18 lines
  [LIB] _decode.py - 104 lines
  [LIB] _encode.py - 85 lines
  [LIB] _format.py - 27 lines
  [LIB] _parse.py - 304 lines
  [LIB] _url.py - 14 lines
ta-lib/venv/lib/python3.10/site-packages/multidict/
  [LIB] __init__.py - 59 lines
  [LIB] _abc.py - 73 lines
  [LIB] _compat.py - 15 lines
  [LIB] _multidict_py.py - 1242 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/
  [CONFIG] __config__.py - 170 lines
  [LIB] __init__.py - 547 lines
  [LIB] _array_api_info.py - 346 lines
  [CONFIG] _configtool.py - 39 lines
  [LIB] _distributor_init.py - 15 lines
  [LIB] _expired_attrs_2_0.py - 80 lines
  [LIB] _globals.py - 95 lines
  [TEST] _pytesttester.py - 200 lines
  [TEST] conftest.py - 261 lines
  [LIB] ctypeslib.py - 602 lines
  [LIB] dtypes.py - 41 lines
  [LIB] exceptions.py - 247 lines
  [LIB] matlib.py - 379 lines
  [LIB] version.py - 11 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/_core/
  [LIB] __init__.py - 180 lines
  [LIB] _add_newdocs.py - 6974 lines
  [LIB] _add_newdocs_scalars.py - 389 lines
  [LIB] _asarray.py - 135 lines
  [LIB] _dtype.py - 374 lines
  [LIB] _dtype_ctypes.py - 120 lines
  [LIB] _exceptions.py - 172 lines
  [LIB] _internal.py - 963 lines
  [EXEC] _machar.py - 356 lines
  [LIB] _methods.py - 256 lines
  [LIB] _string_helpers.py - 100 lines
  [LIB] _type_aliases.py - 119 lines
  [CONFIG] _ufunc_config.py - 483 lines
  [LIB] arrayprint.py - 1756 lines
  [EXEC] cversions.py - 13 lines
  [LIB] defchararray.py - 1414 lines
  [LIB] einsumfunc.py - 1499 lines
  [LIB] fromnumeric.py - 4269 lines
  [LIB] function_base.py - 546 lines
  [LIB] getlimits.py - 747 lines
  [LIB] memmap.py - 361 lines
  [LIB] multiarray.py - 1754 lines
  [LIB] numeric.py - 2713 lines
  [LIB] numerictypes.py - 629 lines
  [LIB] overrides.py - 181 lines
  [LIB] printoptions.py - 32 lines
  [LIB] records.py - 1091 lines
  [LIB] shape_base.py - 1004 lines
  [LIB] strings.py - 1641 lines
  [LIB] umath.py - 40 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/_core/tests/
  [LIB] _locales.py - 72 lines
  [LIB] _natype.py - 198 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/_core/tests/examples/cython/
  [LIB] setup.py - 37 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/_core/tests/examples/limited_api/
  [LIB] setup.py - 22 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/_pyinstaller/
  [LIB] __init__.py - 0 lines
  [LIB] hook-numpy.py - 36 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/_pyinstaller/tests/
  [LIB] __init__.py - 16 lines
  [LIB] pyinstaller-smoke.py - 32 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/_typing/
  [LIB] __init__.py - 154 lines
  [LIB] _add_docstring.py - 153 lines
  [LIB] _array_like.py - 192 lines
  [LIB] _char_codes.py - 214 lines
  [LIB] _dtype_like.py - 249 lines
  [LIB] _extended_precision.py - 27 lines
  [LIB] _nbit.py - 19 lines
  [LIB] _nbit_base.py - 100 lines
  [LIB] _nested_sequence.py - 89 lines
  [LIB] _scalars.py - 27 lines
  [LIB] _shape.py - 7 lines
  [LIB] _ufunc.py - 7 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/_utils/
  [LIB] __init__.py - 88 lines
  [LIB] _convertions.py - 18 lines
  [LIB] _inspect.py - 191 lines
  [LIB] _pep440.py - 487 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/char/
  [LIB] __init__.py - 2 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/compat/
  [LIB] __init__.py - 29 lines
  [LIB] py3k.py - 143 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/compat/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/core/
  [LIB] __init__.py - 32 lines
  [LIB] _dtype.py - 9 lines
  [LIB] _dtype_ctypes.py - 9 lines
  [LIB] _internal.py - 25 lines
  [LIB] _multiarray_umath.py - 55 lines
  [LIB] _utils.py - 21 lines
  [LIB] arrayprint.py - 9 lines
  [LIB] defchararray.py - 9 lines
  [LIB] einsumfunc.py - 9 lines
  [LIB] fromnumeric.py - 9 lines
  [LIB] function_base.py - 9 lines
  [LIB] getlimits.py - 9 lines
  [LIB] multiarray.py - 24 lines
  [LIB] numeric.py - 11 lines
  [LIB] numerictypes.py - 9 lines
  [LIB] overrides.py - 9 lines
  [LIB] records.py - 9 lines
  [LIB] shape_base.py - 9 lines
  [LIB] umath.py - 9 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/distutils/
  [LIB] __init__.py - 64 lines
  [LIB] _shell_utils.py - 87 lines
  [LIB] armccompiler.py - 26 lines
  [LIB] ccompiler.py - 826 lines
  [LIB] ccompiler_opt.py - 2668 lines
  [LIB] conv_template.py - 329 lines
  [LIB] core.py - 215 lines
  [LIB] cpuinfo.py - 683 lines
  [LIB] exec_command.py - 315 lines
  [LIB] extension.py - 101 lines
  [LIB] from_template.py - 261 lines
  [LIB] fujitsuccompiler.py - 28 lines
  [LIB] intelccompiler.py - 106 lines
  [EXEC] lib2def.py - 116 lines
  [LIB] line_endings.py - 77 lines
  [LIB] log.py - 111 lines
  [LIB] mingw32ccompiler.py - 597 lines
  [LIB] misc_util.py - 2484 lines
  [LIB] msvc9compiler.py - 63 lines
  [LIB] msvccompiler.py - 76 lines
  [CONFIG] npy_pkg_config.py - 441 lines
  [LIB] numpy_distribution.py - 17 lines
  [LIB] pathccompiler.py - 21 lines
  [LIB] system_info.py - 3267 lines
  [LIB] unixccompiler.py - 141 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/distutils/command/
  [LIB] __init__.py - 41 lines
  [LIB] autodist.py - 148 lines
  [LIB] bdist_rpm.py - 22 lines
  [LIB] build.py - 62 lines
  [LIB] build_clib.py - 469 lines
  [LIB] build_ext.py - 752 lines
  [LIB] build_py.py - 31 lines
  [LIB] build_scripts.py - 49 lines
  [LIB] build_src.py - 773 lines
  [CONFIG] config.py - 516 lines
  [CONFIG] config_compiler.py - 126 lines
  [LIB] develop.py - 15 lines
  [LIB] egg_info.py - 25 lines
  [LIB] install.py - 79 lines
  [LIB] install_clib.py - 40 lines
  [LIB] install_data.py - 24 lines
  [LIB] install_headers.py - 25 lines
  [LIB] sdist.py - 27 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/distutils/fcompiler/
  [EXEC] __init__.py - 1035 lines
  [EXEC] absoft.py - 156 lines
  [EXEC] arm.py - 71 lines
  [EXEC] compaq.py - 120 lines
  [LIB] environment.py - 88 lines
  [EXEC] fujitsu.py - 46 lines
  [EXEC] g95.py - 42 lines
  [EXEC] gnu.py - 555 lines
  [EXEC] hpux.py - 41 lines
  [EXEC] ibm.py - 97 lines
  [EXEC] intel.py - 211 lines
  [EXEC] lahey.py - 45 lines
  [EXEC] mips.py - 54 lines
  [EXEC] nag.py - 87 lines
  [EXEC] none.py - 28 lines
  [EXEC] nv.py - 53 lines
  [EXEC] pathf95.py - 33 lines
  [EXEC] pg.py - 128 lines
  [EXEC] sun.py - 51 lines
  [EXEC] vast.py - 52 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/distutils/tests/
  [LIB] __init__.py - 0 lines
  [LIB] utilities.py - 90 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/doc/
  [LIB] ufuncs.py - 138 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/f2py/
  [LIB] __init__.py - 87 lines
  [LIB] __main__.py - 5 lines
  [LIB] __version__.py - 1 lines
  [LIB] _isocbind.py - 62 lines
  [LIB] _src_pyf.py - 240 lines
  [LIB] auxfuncs.py - 1000 lines
  [LIB] capi_maps.py - 821 lines
  [LIB] cb_rules.py - 644 lines
  [LIB] cfuncs.py - 1552 lines
  [LIB] common_rules.py - 146 lines
  [LIB] crackfortran.py - 3746 lines
  [LIB] diagnose.py - 154 lines
  [LIB] f2py2e.py - 783 lines
  [LIB] f90mod_rules.py - 270 lines
  [LIB] func2subr.py - 323 lines
  [LIB] rules.py - 1578 lines
  [LIB] symbolic.py - 1517 lines
  [LIB] use_rules.py - 106 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/f2py/_backends/
  [LIB] __init__.py - 9 lines
  [LIB] _backend.py - 46 lines
  [LIB] _distutils.py - 75 lines
  [LIB] _meson.py - 233 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/f2py/tests/
  [LIB] __init__.py - 15 lines
  [LIB] util.py - 441 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/fft/
  [LIB] __init__.py - 215 lines
  [LIB] _helper.py - 235 lines
  [LIB] _pocketfft.py - 1687 lines
  [LIB] helper.py - 16 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/fft/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/lib/
  [LIB] __init__.py - 94 lines
  [LIB] _array_utils_impl.py - 62 lines
  [LIB] _arraypad_impl.py - 891 lines
  [LIB] _arraysetops_impl.py - 1215 lines
  [LIB] _arrayterator_impl.py - 224 lines
  [LIB] _datasource.py - 700 lines
  [LIB] _function_base_impl.py - 5827 lines
  [LIB] _histograms_impl.py - 1090 lines
  [LIB] _index_tricks_impl.py - 1069 lines
  [LIB] _iotools.py - 899 lines
  [LIB] _nanfunctions_impl.py - 2028 lines
  [LIB] _npyio_impl.py - 2595 lines
  [LIB] _polynomial_impl.py - 1458 lines
  [LIB] _scimath_impl.py - 643 lines
  [LIB] _shape_base_impl.py - 1294 lines
  [LIB] _stride_tricks_impl.py - 549 lines
  [LIB] _twodim_base_impl.py - 1188 lines
  [LIB] _type_check_impl.py - 699 lines
  [LIB] _ufunclike_impl.py - 207 lines
  [EXEC] _user_array_impl.py - 291 lines
  [LIB] _utils_impl.py - 775 lines
  [LIB] _version.py - 155 lines
  [LIB] array_utils.py - 7 lines
  [LIB] format.py - 1008 lines
  [LIB] introspect.py - 95 lines
  [LIB] mixins.py - 182 lines
  [LIB] npyio.py - 3 lines
  [LIB] recfunctions.py - 1685 lines
  [LIB] scimath.py - 4 lines
  [LIB] stride_tricks.py - 3 lines
  [LIB] user_array.py - 1 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/lib/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/linalg/
  [LIB] __init__.py - 95 lines
  [LIB] _linalg.py - 3629 lines
  [LIB] linalg.py - 16 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/linalg/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/ma/
  [LIB] __init__.py - 54 lines
  [LIB] core.py - 8959 lines
  [LIB] extras.py - 2321 lines
  [LIB] mrecords.py - 774 lines
  [TEST] testutils.py - 292 lines
  [EXEC] timer_comparison.py - 442 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/ma/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/matrixlib/
  [LIB] __init__.py - 11 lines
  [LIB] defmatrix.py - 1118 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/matrixlib/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/polynomial/
  [LIB] __init__.py - 187 lines
  [LIB] _polybase.py - 1197 lines
  [LIB] chebyshev.py - 2003 lines
  [LIB] hermite.py - 1740 lines
  [LIB] hermite_e.py - 1642 lines
  [LIB] laguerre.py - 1675 lines
  [LIB] legendre.py - 1605 lines
  [LIB] polynomial.py - 1617 lines
  [LIB] polyutils.py - 757 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/polynomial/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/random/
  [LIB] __init__.py - 215 lines
  [LIB] _pickle.py - 89 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/random/_examples/cffi/
  [LIB] extending.py - 40 lines
  [LIB] parse.py - 54 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/random/_examples/numba/
  [LIB] extending.py - 84 lines
  [LIB] extending_distributions.py - 67 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/random/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/random/tests/data/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/rec/
  [LIB] __init__.py - 2 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/strings/
  [LIB] __init__.py - 2 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/testing/
  [LIB] __init__.py - 22 lines
  [LIB] overrides.py - 83 lines
  [EXEC] print_coercion_tables.py - 201 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/testing/_private/
  [LIB] __init__.py - 0 lines
  [LIB] extbuild.py - 252 lines
  [LIB] utils.py - 2760 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/testing/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/typing/
  [LIB] __init__.py - 175 lines
  [LIB] mypy_plugin.py - 199 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/typing/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/numpy/typing/tests/data/pass/
  [LIB] arithmetic.py - 596 lines
  [LIB] array_constructors.py - 137 lines
  [LIB] array_like.py - 45 lines
  [LIB] arrayprint.py - 37 lines
  [LIB] arrayterator.py - 27 lines
  [LIB] bitwise_ops.py - 131 lines
  [LIB] comparisons.py - 315 lines
  [LIB] dtype.py - 57 lines
  [LIB] einsumfunc.py - 36 lines
  [LIB] flatiter.py - 16 lines
  [LIB] fromnumeric.py - 272 lines
  [LIB] index_tricks.py - 60 lines
  [LIB] lib_user_array.py - 22 lines
  [LIB] lib_utils.py - 19 lines
  [LIB] lib_version.py - 18 lines
  [LIB] literal.py - 51 lines
  [LIB] ma.py - 8 lines
  [LIB] mod.py - 149 lines
  [LIB] modules.py - 45 lines
  [LIB] multiarray.py - 76 lines
  [LIB] ndarray_conversion.py - 87 lines
  [LIB] ndarray_misc.py - 196 lines
  [LIB] ndarray_shape_manipulation.py - 47 lines
  [LIB] nditer.py - 4 lines
  [LIB] numeric.py - 95 lines
  [LIB] numerictypes.py - 17 lines
  [LIB] random.py - 1497 lines
  [LIB] recfunctions.py - 162 lines
  [LIB] scalars.py - 248 lines
  [LIB] shape.py - 21 lines
  [LIB] simple.py - 168 lines
  [LIB] simple_py3.py - 6 lines
  [CONFIG] ufunc_config.py - 64 lines
  [LIB] ufunclike.py - 47 lines
  [LIB] ufuncs.py - 16 lines
  [LIB] warnings_and_errors.py - 6 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/
  [LIB] __init__.py - 367 lines
  [LIB] _typing.py - 525 lines
  [LIB] _version.py - 692 lines
  [LIB] _version_meson.py - 2 lines
  [TEST] conftest.py - 2065 lines
  [TEST] testing.py - 18 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/_config/
  [LIB] __init__.py - 57 lines
  [CONFIG] config.py - 948 lines
  [LIB] dates.py - 25 lines
  [LIB] display.py - 62 lines
  [LIB] localization.py - 172 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/_libs/
  [LIB] __init__.py - 27 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/_libs/tslibs/
  [LIB] __init__.py - 87 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/_libs/window/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/_testing/
  [LIB] __init__.py - 635 lines
  [LIB] _hypothesis.py - 93 lines
  [LIB] _io.py - 170 lines
  [LIB] _warnings.py - 232 lines
  [LIB] asserters.py - 1459 lines
  [LIB] compat.py - 29 lines
  [LIB] contexts.py - 258 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/api/
  [LIB] __init__.py - 16 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/api/extensions/
  [LIB] __init__.py - 33 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/api/indexers/
  [LIB] __init__.py - 17 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/api/interchange/
  [LIB] __init__.py - 8 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/api/types/
  [LIB] __init__.py - 23 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/api/typing/
  [LIB] __init__.py - 55 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/arrays/
  [LIB] __init__.py - 53 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/compat/
  [LIB] __init__.py - 209 lines
  [LIB] _constants.py - 30 lines
  [LIB] _optional.py - 168 lines
  [LIB] compressors.py - 77 lines
  [LIB] pickle_compat.py - 262 lines
  [LIB] pyarrow.py - 39 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/compat/numpy/
  [LIB] __init__.py - 53 lines
  [LIB] function.py - 418 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/
  [LIB] __init__.py - 0 lines
  [LIB] accessor.py - 340 lines
  [LIB] algorithms.py - 1747 lines
  [LIB] api.py - 140 lines
  [LIB] apply.py - 2057 lines
  [LIB] arraylike.py - 530 lines
  [LIB] base.py - 1400 lines
  [LIB] common.py - 657 lines
  [CONFIG] config_init.py - 941 lines
  [LIB] construction.py - 821 lines
  [LIB] flags.py - 117 lines
  [LIB] frame.py - 12704 lines
  [LIB] generic.py - 13979 lines
  [LIB] indexing.py - 2785 lines
  [LIB] missing.py - 1158 lines
  [LIB] nanops.py - 1748 lines
  [LIB] resample.py - 2920 lines
  [LIB] roperator.py - 62 lines
  [LIB] sample.py - 154 lines
  [LIB] series.py - 6642 lines
  [LIB] shared_docs.py - 952 lines
  [LIB] sorting.py - 748 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/_numba/
  [LIB] __init__.py - 0 lines
  [LIB] executor.py - 239 lines
  [LIB] extensions.py - 585 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/_numba/kernels/
  [LIB] __init__.py - 27 lines
  [LIB] mean_.py - 196 lines
  [LIB] min_max_.py - 125 lines
  [LIB] shared.py - 29 lines
  [LIB] sum_.py - 244 lines
  [LIB] var_.py - 245 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/array_algos/
  [LIB] __init__.py - 9 lines
  [LIB] datetimelike_accumulations.py - 67 lines
  [LIB] masked_accumulations.py - 90 lines
  [LIB] masked_reductions.py - 201 lines
  [LIB] putmask.py - 149 lines
  [LIB] quantile.py - 226 lines
  [LIB] replace.py - 154 lines
  [LIB] take.py - 594 lines
  [LIB] transforms.py - 50 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/arrays/
  [LIB] __init__.py - 43 lines
  [LIB] _arrow_string_mixins.py - 356 lines
  [LIB] _mixins.py - 544 lines
  [LIB] _ranges.py - 207 lines
  [LIB] _utils.py - 63 lines
  [LIB] base.py - 2609 lines
  [LIB] boolean.py - 407 lines
  [LIB] categorical.py - 3103 lines
  [LIB] datetimelike.py - 2583 lines
  [LIB] datetimes.py - 2837 lines
  [LIB] floating.py - 173 lines
  [LIB] integer.py - 272 lines
  [LIB] interval.py - 1930 lines
  [LIB] masked.py - 1669 lines
  [LIB] numeric.py - 286 lines
  [LIB] numpy_.py - 574 lines
  [LIB] period.py - 1331 lines
  [LIB] string_.py - 1110 lines
  [LIB] string_arrow.py - 493 lines
  [LIB] timedeltas.py - 1185 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/arrays/arrow/
  [LIB] __init__.py - 7 lines
  [LIB] _arrow_utils.py - 50 lines
  [LIB] accessors.py - 473 lines
  [LIB] array.py - 2927 lines
  [LIB] extension_types.py - 174 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/arrays/sparse/
  [LIB] __init__.py - 19 lines
  [LIB] accessor.py - 414 lines
  [LIB] array.py - 1945 lines
  [LIB] scipy_sparse.py - 207 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/computation/
  [LIB] __init__.py - 0 lines
  [LIB] align.py - 213 lines
  [LIB] api.py - 2 lines
  [LIB] check.py - 8 lines
  [LIB] common.py - 48 lines
  [LIB] engines.py - 143 lines
  [LIB] eval.py - 421 lines
  [LIB] expr.py - 840 lines
  [LIB] expressions.py - 286 lines
  [LIB] ops.py - 572 lines
  [LIB] parsing.py - 198 lines
  [LIB] pytables.py - 666 lines
  [LIB] scope.py - 355 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/dtypes/
  [LIB] __init__.py - 0 lines
  [LIB] api.py - 85 lines
  [LIB] astype.py - 301 lines
  [LIB] base.py - 583 lines
  [LIB] cast.py - 1988 lines
  [LIB] common.py - 1766 lines
  [LIB] concat.py - 348 lines
  [LIB] dtypes.py - 2348 lines
  [LIB] generic.py - 147 lines
  [LIB] inference.py - 437 lines
  [LIB] missing.py - 810 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/groupby/
  [LIB] __init__.py - 15 lines
  [LIB] base.py - 121 lines
  [LIB] categorical.py - 87 lines
  [LIB] generic.py - 2852 lines
  [LIB] groupby.py - 6003 lines
  [LIB] grouper.py - 1102 lines
  [LIB] indexing.py - 304 lines
  [LIB] numba_.py - 181 lines
  [LIB] ops.py - 1208 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/indexers/
  [LIB] __init__.py - 31 lines
  [LIB] objects.py - 453 lines
  [LIB] utils.py - 553 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/indexes/
  [LIB] __init__.py - 0 lines
  [LIB] accessors.py - 643 lines
  [LIB] api.py - 388 lines
  [LIB] base.py - 7943 lines
  [LIB] category.py - 513 lines
  [LIB] datetimelike.py - 843 lines
  [LIB] datetimes.py - 1127 lines
  [LIB] extension.py - 172 lines
  [LIB] frozen.py - 120 lines
  [LIB] interval.py - 1137 lines
  [LIB] multi.py - 4176 lines
  [LIB] period.py - 614 lines
  [LIB] range.py - 1187 lines
  [LIB] timedeltas.py - 356 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/interchange/
  [LIB] __init__.py - 0 lines
  [LIB] buffer.py - 136 lines
  [LIB] column.py - 461 lines
  [LIB] dataframe.py - 113 lines
  [LIB] dataframe_protocol.py - 465 lines
  [LIB] from_dataframe.py - 557 lines
  [LIB] utils.py - 183 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/internals/
  [LIB] __init__.py - 85 lines
  [LIB] api.py - 156 lines
  [LIB] array_manager.py - 1340 lines
  [LIB] base.py - 407 lines
  [LIB] blocks.py - 2923 lines
  [LIB] concat.py - 598 lines
  [LIB] construction.py - 1073 lines
  [LIB] managers.py - 2375 lines
  [LIB] ops.py - 154 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/methods/
  [LIB] __init__.py - 0 lines
  [LIB] describe.py - 416 lines
  [LIB] selectn.py - 269 lines
  [LIB] to_dict.py - 272 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/ops/
  [LIB] __init__.py - 93 lines
  [LIB] array_ops.py - 604 lines
  [LIB] common.py - 146 lines
  [LIB] dispatch.py - 30 lines
  [LIB] docstrings.py - 772 lines
  [LIB] invalid.py - 62 lines
  [LIB] mask_ops.py - 189 lines
  [LIB] missing.py - 176 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/reshape/
  [LIB] __init__.py - 0 lines
  [LIB] api.py - 41 lines
  [LIB] concat.py - 894 lines
  [LIB] encoding.py - 571 lines
  [LIB] melt.py - 512 lines
  [LIB] merge.py - 2762 lines
  [LIB] pivot.py - 899 lines
  [LIB] reshape.py - 989 lines
  [LIB] tile.py - 638 lines
  [LIB] util.py - 85 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/sparse/
  [LIB] __init__.py - 0 lines
  [LIB] api.py - 5 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/strings/
  [LIB] __init__.py - 28 lines
  [LIB] accessor.py - 3571 lines
  [LIB] base.py - 266 lines
  [LIB] object_array.py - 534 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/tools/
  [LIB] __init__.py - 0 lines
  [LIB] datetimes.py - 1240 lines
  [LIB] numeric.py - 332 lines
  [LIB] timedeltas.py - 283 lines
  [LIB] times.py - 168 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/util/
  [LIB] __init__.py - 0 lines
  [LIB] hashing.py - 339 lines
  [LIB] numba_.py - 98 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/core/window/
  [LIB] __init__.py - 23 lines
  [LIB] common.py - 169 lines
  [LIB] doc.py - 116 lines
  [LIB] ewm.py - 1095 lines
  [LIB] expanding.py - 964 lines
  [LIB] numba_.py - 351 lines
  [LIB] online.py - 118 lines
  [LIB] rolling.py - 2930 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/errors/
  [LIB] __init__.py - 850 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/io/
  [LIB] __init__.py - 13 lines
  [LIB] _util.py - 94 lines
  [LIB] api.py - 65 lines
  [LIB] clipboards.py - 197 lines
  [LIB] common.py - 1267 lines
  [LIB] feather_format.py - 130 lines
  [LIB] gbq.py - 255 lines
  [LIB] html.py - 1259 lines
  [LIB] orc.py - 228 lines
  [LIB] parquet.py - 678 lines
  [LIB] pickle.py - 210 lines
  [LIB] pytables.py - 5532 lines
  [LIB] spss.py - 72 lines
  [LIB] sql.py - 2916 lines
  [LIB] stata.py - 3768 lines
  [LIB] xml.py - 1177 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/io/clipboard/
  [LIB] __init__.py - 747 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/io/excel/
  [LIB] __init__.py - 19 lines
  [LIB] _base.py - 1659 lines
  [LIB] _calamine.py - 121 lines
  [LIB] _odfreader.py - 253 lines
  [LIB] _odswriter.py - 357 lines
  [LIB] _openpyxl.py - 639 lines
  [LIB] _pyxlsb.py - 127 lines
  [LIB] _util.py - 334 lines
  [LIB] _xlrd.py - 143 lines
  [LIB] _xlsxwriter.py - 284 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/io/formats/
  [LIB] __init__.py - 9 lines
  [LIB] _color_data.py - 157 lines
  [LIB] console.py - 94 lines
  [LIB] css.py - 421 lines
  [LIB] csvs.py - 330 lines
  [LIB] excel.py - 962 lines
  [LIB] format.py - 2058 lines
  [LIB] html.py - 646 lines
  [LIB] info.py - 1101 lines
  [LIB] printing.py - 572 lines
  [LIB] string.py - 206 lines
  [LIB] style.py - 4136 lines
  [LIB] style_render.py - 2497 lines
  [LIB] xml.py - 560 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/io/json/
  [LIB] __init__.py - 15 lines
  [LIB] _json.py - 1494 lines
  [LIB] _normalize.py - 544 lines
  [LIB] _table_schema.py - 389 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/io/parsers/
  [LIB] __init__.py - 9 lines
  [LIB] arrow_parser_wrapper.py - 295 lines
  [LIB] base_parser.py - 1462 lines
  [LIB] c_parser_wrapper.py - 410 lines
  [LIB] python_parser.py - 1387 lines
  [LIB] readers.py - 2383 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/io/sas/
  [LIB] __init__.py - 3 lines
  [LIB] sas7bdat.py - 762 lines
  [LIB] sas_constants.py - 310 lines
  [LIB] sas_xport.py - 508 lines
  [LIB] sasreader.py - 178 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/plotting/
  [LIB] __init__.py - 98 lines
  [LIB] _core.py - 1946 lines
  [LIB] _misc.py - 688 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/plotting/_matplotlib/
  [LIB] __init__.py - 93 lines
  [LIB] boxplot.py - 575 lines
  [LIB] converter.py - 1139 lines
  [LIB] core.py - 2125 lines
  [LIB] groupby.py - 142 lines
  [LIB] hist.py - 581 lines
  [LIB] misc.py - 481 lines
  [LIB] style.py - 278 lines
  [LIB] timeseries.py - 370 lines
  [LIB] tools.py - 492 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/api/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/apply/
  [LIB] __init__.py - 0 lines
  [LIB] common.py - 7 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arithmetic/
  [LIB] __init__.py - 0 lines
  [LIB] common.py - 155 lines
  [TEST] conftest.py - 139 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/
  [LIB] __init__.py - 0 lines
  [LIB] masked_shared.py - 154 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/boolean/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/categorical/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/datetimes/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/floating/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 48 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/integer/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 68 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/interval/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/masked/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/numpy_/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/period/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/sparse/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/string_/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/arrays/timedeltas/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/base/
  [LIB] __init__.py - 0 lines
  [LIB] common.py - 9 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/computation/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/config/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/construction/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/copy_view/
  [LIB] __init__.py - 0 lines
  [LIB] util.py - 30 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/copy_view/index/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/dtypes/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/dtypes/cast/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/extension/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 230 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/extension/array_with_attr/
  [LIB] __init__.py - 6 lines
  [LIB] array.py - 89 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/extension/base/
  [LIB] __init__.py - 131 lines
  [LIB] accumulate.py - 40 lines
  [LIB] base.py - 2 lines
  [LIB] casting.py - 87 lines
  [LIB] constructors.py - 142 lines
  [LIB] dim2.py - 345 lines
  [LIB] dtype.py - 123 lines
  [LIB] getitem.py - 469 lines
  [LIB] groupby.py - 174 lines
  [LIB] index.py - 19 lines
  [LIB] interface.py - 172 lines
  [LIB] io.py - 39 lines
  [LIB] methods.py - 720 lines
  [LIB] missing.py - 190 lines
  [LIB] ops.py - 289 lines
  [LIB] printing.py - 41 lines
  [LIB] reduce.py - 153 lines
  [LIB] reshaping.py - 379 lines
  [LIB] setitem.py - 451 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/extension/date/
  [LIB] __init__.py - 6 lines
  [LIB] array.py - 188 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/extension/decimal/
  [LIB] __init__.py - 8 lines
  [LIB] array.py - 311 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/extension/json/
  [LIB] __init__.py - 7 lines
  [LIB] array.py - 273 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/extension/list/
  [LIB] __init__.py - 7 lines
  [LIB] array.py - 137 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/frame/
  [LIB] __init__.py - 0 lines
  [LIB] common.py - 63 lines
  [TEST] conftest.py - 100 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/frame/constructors/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/frame/indexing/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/frame/methods/
  [LIB] __init__.py - 7 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/generic/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/groupby/
  [LIB] __init__.py - 25 lines
  [TEST] conftest.py - 208 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/groupby/aggregate/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/groupby/methods/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/groupby/transform/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 41 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/base_class/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/categorical/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/datetimelike_/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/datetimes/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/datetimes/methods/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/interval/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/multi/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 27 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/numeric/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/object/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/period/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/period/methods/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/ranges/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/string/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/timedeltas/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexes/timedeltas/methods/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexing/
  [LIB] __init__.py - 0 lines
  [LIB] common.py - 40 lines
  [TEST] conftest.py - 127 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexing/interval/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/indexing/multiindex/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/interchange/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/internals/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 225 lines (ports: 5000)
  [LIB] generate_legacy_storage_files.py - 350 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/excel/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/formats/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/formats/style/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/json/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 9 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/parser/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 337 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/parser/common/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/parser/dtypes/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/parser/usecols/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/pytables/
  [LIB] __init__.py - 0 lines
  [LIB] common.py - 50 lines
  [TEST] conftest.py - 9 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/sas/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/io/xml/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 38 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/libs/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/plotting/
  [LIB] __init__.py - 0 lines
  [LIB] common.py - 563 lines
  [TEST] conftest.py - 56 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/plotting/frame/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/reductions/
  [LIB] __init__.py - 4 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/resample/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 143 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/reshape/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/reshape/concat/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 7 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/reshape/merge/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/scalar/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/scalar/interval/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/scalar/period/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/scalar/timedelta/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/scalar/timedelta/methods/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/scalar/timestamp/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/scalar/timestamp/methods/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/series/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/series/accessors/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/series/indexing/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/series/methods/
  [LIB] __init__.py - 7 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/strings/
  [LIB] __init__.py - 23 lines
  [TEST] conftest.py - 132 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/tools/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/tseries/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/tseries/frequencies/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/tseries/holiday/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/tseries/offsets/
  [LIB] __init__.py - 0 lines
  [LIB] common.py - 37 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/tslibs/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/util/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 26 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/window/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 146 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tests/window/moments/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 72 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/tseries/
  [LIB] __init__.py - 12 lines
  [LIB] api.py - 10 lines
  [LIB] frequencies.py - 602 lines
  [LIB] holiday.py - 634 lines
  [LIB] offsets.py - 91 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/util/
  [LIB] __init__.py - 29 lines
  [LIB] _decorators.py - 508 lines
  [LIB] _doctools.py - 202 lines
  [LIB] _exceptions.py - 103 lines
  [LIB] _print_versions.py - 158 lines
  [TEST] _test_decorators.py - 173 lines
  [TEST] _tester.py - 53 lines
  [LIB] _validators.py - 456 lines
ta-lib/venv/lib/python3.10/site-packages/pandas/util/version/
  [LIB] __init__.py - 579 lines
ta-lib/venv/lib/python3.10/site-packages/pip/
  [LIB] __init__.py - 13 lines
  [LIB] __main__.py - 31 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/
  [LIB] __init__.py - 19 lines
  [LIB] build_env.py - 296 lines
  [LIB] cache.py - 264 lines
  [CONFIG] configuration.py - 366 lines
  [LIB] exceptions.py - 658 lines
  [LIB] main.py - 12 lines
  [LIB] pyproject.py - 168 lines
  [LIB] self_outdated_check.py - 189 lines
  [LIB] wheel_builder.py - 377 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/cli/
  [LIB] __init__.py - 4 lines
  [LIB] autocompletion.py - 171 lines
  [LIB] base_command.py - 220 lines
  [LIB] cmdoptions.py - 1018 lines
  [LIB] command_context.py - 27 lines
  [LIB] main.py - 70 lines
  [LIB] main_parser.py - 87 lines
  [LIB] parser.py - 292 lines
  [LIB] progress_bars.py - 321 lines
  [LIB] req_command.py - 506 lines
  [LIB] spinners.py - 157 lines
  [LIB] status_codes.py - 6 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/commands/
  [LIB] __init__.py - 127 lines
  [LIB] cache.py - 223 lines
  [LIB] check.py - 53 lines
  [LIB] completion.py - 96 lines
  [CONFIG] configuration.py - 266 lines
  [LIB] debug.py - 202 lines
  [LIB] download.py - 140 lines
  [LIB] freeze.py - 97 lines
  [LIB] hash.py - 59 lines
  [LIB] help.py - 41 lines
  [LIB] index.py - 139 lines
  [LIB] install.py - 771 lines
  [LIB] list.py - 363 lines
  [LIB] search.py - 174 lines
  [LIB] show.py - 178 lines
  [LIB] uninstall.py - 105 lines
  [LIB] wheel.py - 178 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/distributions/
  [LIB] __init__.py - 21 lines
  [LIB] base.py - 36 lines
  [LIB] installed.py - 20 lines
  [LIB] sdist.py - 127 lines
  [LIB] wheel.py - 31 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/index/
  [LIB] __init__.py - 2 lines
  [LIB] collector.py - 648 lines
  [LIB] package_finder.py - 1004 lines
  [LIB] sources.py - 224 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/locations/
  [LIB] __init__.py - 520 lines
  [LIB] _distutils.py - 169 lines
  [CONFIG] _sysconfig.py - 219 lines
  [LIB] base.py - 52 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/metadata/
  [LIB] __init__.py - 62 lines
  [LIB] base.py - 546 lines
  [LIB] pkg_resources.py - 256 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/models/
  [LIB] __init__.py - 2 lines
  [LIB] candidate.py - 34 lines
  [LIB] direct_url.py - 220 lines
  [LIB] format_control.py - 80 lines
  [LIB] index.py - 28 lines
  [LIB] link.py - 288 lines
  [LIB] scheme.py - 31 lines
  [LIB] search_scope.py - 129 lines
  [LIB] selection_prefs.py - 51 lines
  [LIB] target_python.py - 110 lines
  [LIB] wheel.py - 89 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/network/
  [LIB] __init__.py - 2 lines
  [LIB] auth.py - 323 lines
  [LIB] cache.py - 69 lines
  [LIB] download.py - 185 lines
  [LIB] lazy_wheel.py - 210 lines
  [LIB] session.py - 454 lines
  [LIB] utils.py - 96 lines
  [LIB] xmlrpc.py - 60 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/operations/
  [LIB] __init__.py - 0 lines
  [LIB] check.py - 149 lines
  [LIB] freeze.py - 254 lines
  [LIB] prepare.py - 642 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/operations/build/
  [LIB] __init__.py - 0 lines
  [LIB] metadata.py - 39 lines
  [LIB] metadata_editable.py - 41 lines
  [LIB] metadata_legacy.py - 74 lines
  [LIB] wheel.py - 37 lines
  [LIB] wheel_editable.py - 46 lines
  [LIB] wheel_legacy.py - 102 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/operations/install/
  [LIB] __init__.py - 2 lines
  [LIB] editable_legacy.py - 47 lines
  [LIB] legacy.py - 120 lines
  [LIB] wheel.py - 738 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/req/
  [LIB] __init__.py - 94 lines
  [LIB] constructors.py - 490 lines
  [LIB] req_file.py - 536 lines
  [LIB] req_install.py - 858 lines
  [LIB] req_set.py - 189 lines
  [LIB] req_tracker.py - 124 lines
  [LIB] req_uninstall.py - 633 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/resolution/
  [LIB] __init__.py - 0 lines
  [LIB] base.py - 20 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/resolution/legacy/
  [LIB] __init__.py - 0 lines
  [LIB] resolver.py - 467 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/resolution/resolvelib/
  [LIB] __init__.py - 0 lines
  [LIB] base.py - 141 lines
  [LIB] candidates.py - 547 lines
  [LIB] factory.py - 739 lines
  [LIB] found_candidates.py - 155 lines
  [LIB] provider.py - 248 lines
  [LIB] reporter.py - 68 lines
  [LIB] requirements.py - 166 lines
  [LIB] resolver.py - 292 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/utils/
  [LIB] __init__.py - 0 lines
  [LIB] _log.py - 38 lines
  [LIB] appdirs.py - 52 lines
  [LIB] compat.py - 63 lines
  [LIB] compatibility_tags.py - 165 lines
  [LIB] datetime.py - 11 lines
  [LIB] deprecation.py - 120 lines
  [LIB] direct_url_helpers.py - 87 lines
  [LIB] distutils_args.py - 42 lines
  [LIB] egg_link.py - 75 lines
  [LIB] encoding.py - 36 lines
  [LIB] entrypoints.py - 27 lines
  [LIB] filesystem.py - 182 lines
  [LIB] filetypes.py - 27 lines
  [LIB] glibc.py - 88 lines
  [LIB] hashes.py - 144 lines
  [LIB] inject_securetransport.py - 35 lines
  [LIB] logging.py - 343 lines
  [LIB] misc.py - 653 lines
  [LIB] models.py - 39 lines
  [LIB] packaging.py - 57 lines
  [LIB] setuptools_build.py - 195 lines
  [LIB] subprocess.py - 260 lines
  [LIB] temp_dir.py - 246 lines
  [LIB] unpacking.py - 258 lines
  [LIB] urls.py - 62 lines
  [LIB] virtualenv.py - 104 lines
  [LIB] wheel.py - 136 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_internal/vcs/
  [LIB] __init__.py - 15 lines
  [LIB] bazaar.py - 101 lines
  [LIB] git.py - 526 lines
  [LIB] mercurial.py - 163 lines
  [LIB] subversion.py - 324 lines
  [LIB] versioncontrol.py - 705 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/
  [LIB] __init__.py - 111 lines
  [LIB] distro.py - 1386 lines
  [LIB] six.py - 998 lines
  [LIB] typing_extensions.py - 2296 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/cachecontrol/
  [LIB] __init__.py - 18 lines
  [LIB] _cmd.py - 61 lines
  [LIB] adapter.py - 137 lines
  [LIB] cache.py - 43 lines
  [LIB] compat.py - 32 lines
  [LIB] controller.py - 415 lines
  [LIB] filewrapper.py - 111 lines
  [LIB] heuristics.py - 139 lines
  [LIB] serialize.py - 186 lines
  [LIB] wrapper.py - 33 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/cachecontrol/caches/
  [LIB] __init__.py - 6 lines
  [LIB] file_cache.py - 150 lines
  [LIB] redis_cache.py - 37 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/certifi/
  [LIB] __init__.py - 3 lines
  [LIB] __main__.py - 12 lines
  [LIB] core.py - 76 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/chardet/
  [LIB] __init__.py - 83 lines
  [LIB] big5freq.py - 386 lines
  [LIB] big5prober.py - 47 lines
  [LIB] chardistribution.py - 233 lines
  [LIB] charsetgroupprober.py - 107 lines
  [LIB] charsetprober.py - 145 lines
  [LIB] codingstatemachine.py - 88 lines
  [LIB] compat.py - 36 lines
  [LIB] cp949prober.py - 49 lines
  [LIB] enums.py - 76 lines
  [LIB] escprober.py - 101 lines
  [LIB] escsm.py - 246 lines
  [LIB] eucjpprober.py - 92 lines
  [LIB] euckrfreq.py - 195 lines
  [LIB] euckrprober.py - 47 lines
  [LIB] euctwfreq.py - 387 lines
  [LIB] euctwprober.py - 46 lines
  [LIB] gb2312freq.py - 283 lines
  [LIB] gb2312prober.py - 46 lines
  [LIB] hebrewprober.py - 292 lines
  [LIB] jisfreq.py - 325 lines
  [LIB] jpcntx.py - 233 lines
  [LIB] langbulgarianmodel.py - 4650 lines
  [LIB] langgreekmodel.py - 4398 lines
  [LIB] langhebrewmodel.py - 4383 lines
  [LIB] langhungarianmodel.py - 4650 lines
  [LIB] langrussianmodel.py - 5718 lines
  [LIB] langthaimodel.py - 4383 lines
  [LIB] langturkishmodel.py - 4383 lines
  [LIB] latin1prober.py - 145 lines
  [LIB] mbcharsetprober.py - 91 lines
  [LIB] mbcsgroupprober.py - 54 lines
  [LIB] mbcssm.py - 572 lines
  [LIB] sbcharsetprober.py - 145 lines
  [LIB] sbcsgroupprober.py - 83 lines
  [LIB] sjisprober.py - 92 lines
  [LIB] universaldetector.py - 286 lines
  [LIB] utf8prober.py - 82 lines
  [LIB] version.py - 9 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/chardet/cli/
  [LIB] __init__.py - 1 lines
  [EXEC] chardetect.py - 84 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/chardet/metadata/
  [LIB] __init__.py - 0 lines
  [LIB] languages.py - 310 lines (ports: 1993)
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/colorama/
  [LIB] __init__.py - 6 lines
  [LIB] ansi.py - 102 lines
  [LIB] ansitowin32.py - 258 lines
  [LIB] initialise.py - 80 lines
  [LIB] win32.py - 152 lines
  [LIB] winterm.py - 169 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/distlib/
  [LIB] __init__.py - 23 lines
  [LIB] compat.py - 1116 lines
  [LIB] database.py - 1345 lines
  [LIB] index.py - 509 lines
  [LIB] locators.py - 1300 lines
  [LIB] manifest.py - 393 lines
  [LIB] markers.py - 152 lines
  [LIB] metadata.py - 1058 lines
  [LIB] resources.py - 358 lines
  [EXEC] scripts.py - 429 lines
  [LIB] util.py - 1932 lines
  [LIB] version.py - 739 lines
  [LIB] wheel.py - 1053 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/html5lib/
  [LIB] __init__.py - 35 lines
  [LIB] _ihatexml.py - 289 lines
  [LIB] _inputstream.py - 918 lines
  [LIB] _tokenizer.py - 1735 lines
  [LIB] _utils.py - 159 lines
  [LIB] constants.py - 2946 lines
  [LIB] html5parser.py - 2795 lines
  [LIB] serializer.py - 409 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/html5lib/_trie/
  [LIB] __init__.py - 5 lines
  [LIB] _base.py - 40 lines
  [LIB] py.py - 67 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/html5lib/filters/
  [LIB] __init__.py - 0 lines
  [LIB] alphabeticalattributes.py - 29 lines
  [LIB] base.py - 12 lines
  [LIB] inject_meta_charset.py - 73 lines
  [LIB] lint.py - 93 lines
  [LIB] optionaltags.py - 207 lines
  [LIB] sanitizer.py - 916 lines
  [LIB] whitespace.py - 38 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/html5lib/treeadapters/
  [LIB] __init__.py - 30 lines
  [LIB] genshi.py - 54 lines
  [LIB] sax.py - 50 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/html5lib/treebuilders/
  [LIB] __init__.py - 88 lines
  [LIB] base.py - 417 lines
  [LIB] dom.py - 239 lines
  [LIB] etree.py - 343 lines
  [LIB] etree_lxml.py - 392 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/html5lib/treewalkers/
  [LIB] __init__.py - 154 lines
  [LIB] base.py - 252 lines
  [LIB] dom.py - 43 lines
  [LIB] etree.py - 131 lines
  [LIB] etree_lxml.py - 215 lines
  [LIB] genshi.py - 69 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/idna/
  [LIB] __init__.py - 44 lines
  [LIB] codec.py - 112 lines
  [LIB] compat.py - 13 lines
  [LIB] core.py - 397 lines
  [LIB] idnadata.py - 2137 lines
  [LIB] intranges.py - 54 lines
  [LIB] package_data.py - 2 lines
  [LIB] uts46data.py - 8512 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/msgpack/
  [LIB] __init__.py - 54 lines
  [LIB] _version.py - 1 lines
  [LIB] exceptions.py - 48 lines
  [LIB] ext.py - 193 lines
  [LIB] fallback.py - 1012 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/packaging/
  [LIB] __about__.py - 26 lines
  [LIB] __init__.py - 25 lines
  [LIB] _manylinux.py - 301 lines
  [LIB] _musllinux.py - 136 lines
  [LIB] _structures.py - 61 lines
  [LIB] markers.py - 304 lines
  [LIB] requirements.py - 146 lines
  [LIB] specifiers.py - 802 lines
  [LIB] tags.py - 487 lines
  [LIB] utils.py - 136 lines
  [LIB] version.py - 504 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/pep517/
  [LIB] __init__.py - 6 lines
  [EXEC] build.py - 127 lines
  [EXEC] check.py - 207 lines
  [LIB] colorlog.py - 115 lines
  [LIB] compat.py - 51 lines
  [LIB] dirtools.py - 44 lines
  [LIB] envbuild.py - 171 lines
  [EXEC] meta.py - 92 lines
  [LIB] wrappers.py - 375 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/pep517/in_process/
  [LIB] __init__.py - 17 lines
  [EXEC] _in_process.py - 363 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/pkg_resources/
  [LIB] __init__.py - 3296 lines
  [LIB] py31compat.py - 23 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/platformdirs/
  [LIB] __init__.py - 331 lines
  [LIB] __main__.py - 46 lines
  [LIB] android.py - 119 lines
  [LIB] api.py - 156 lines
  [LIB] macos.py - 64 lines
  [LIB] unix.py - 181 lines
  [LIB] version.py - 4 lines
  [LIB] windows.py - 182 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/progress/
  [LIB] __init__.py - 189 lines
  [LIB] bar.py - 93 lines
  [LIB] colors.py - 79 lines
  [LIB] counter.py - 47 lines
  [LIB] spinner.py - 45 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/pygments/
  [LIB] __init__.py - 83 lines
  [LIB] __main__.py - 17 lines
  [LIB] cmdline.py - 663 lines
  [LIB] console.py - 70 lines
  [LIB] filter.py - 71 lines
  [LIB] formatter.py - 94 lines
  [LIB] lexer.py - 879 lines (ports: 1024)
  [LIB] modeline.py - 43 lines
  [LIB] plugin.py - 69 lines
  [LIB] regexopt.py - 91 lines
  [LIB] scanner.py - 104 lines
  [LIB] sphinxext.py - 155 lines
  [LIB] style.py - 197 lines
  [LIB] token.py - 212 lines
  [EXEC] unistring.py - 153 lines
  [LIB] util.py - 308 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/pygments/filters/
  [LIB] __init__.py - 937 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/pygments/formatters/
  [LIB] __init__.py - 153 lines
  [EXEC] _mapping.py - 84 lines
  [LIB] bbcode.py - 108 lines
  [LIB] groff.py - 168 lines
  [LIB] html.py - 983 lines
  [LIB] img.py - 641 lines
  [LIB] irc.py - 179 lines
  [LIB] latex.py - 511 lines
  [LIB] other.py - 161 lines
  [LIB] pangomarkup.py - 83 lines
  [LIB] rtf.py - 146 lines
  [LIB] svg.py - 188 lines
  [LIB] terminal.py - 127 lines
  [LIB] terminal256.py - 338 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/pygments/lexers/
  [LIB] __init__.py - 341 lines
  [EXEC] _mapping.py - 580 lines
  [LIB] python.py - 1188 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/pygments/styles/
  [LIB] __init__.py - 93 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/pyparsing/
  [LIB] __init__.py - 328 lines
  [LIB] actions.py - 207 lines
  [LIB] common.py - 424 lines
  [LIB] core.py - 5789 lines
  [LIB] exceptions.py - 267 lines
  [LIB] helpers.py - 1069 lines
  [LIB] results.py - 760 lines
  [TEST] testing.py - 331 lines
  [LIB] unicode.py - 332 lines
  [LIB] util.py - 235 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/pyparsing/diagram/
  [LIB] __init__.py - 593 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/requests/
  [LIB] __init__.py - 154 lines
  [LIB] __version__.py - 14 lines
  [LIB] _internal_utils.py - 42 lines
  [LIB] adapters.py - 538 lines
  [LIB] api.py - 159 lines
  [LIB] auth.py - 305 lines
  [EXEC] certs.py - 18 lines
  [LIB] compat.py - 77 lines
  [LIB] cookies.py - 549 lines
  [LIB] exceptions.py - 133 lines
  [EXEC] help.py - 132 lines
  [LIB] hooks.py - 34 lines
  [LIB] models.py - 973 lines
  [LIB] packages.py - 16 lines
  [LIB] sessions.py - 771 lines (ports: 3128,4012)
  [LIB] status_codes.py - 123 lines
  [LIB] structures.py - 105 lines
  [LIB] utils.py - 1060 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/resolvelib/
  [LIB] __init__.py - 26 lines
  [LIB] providers.py - 133 lines
  [LIB] reporters.py - 43 lines
  [LIB] resolvers.py - 482 lines
  [LIB] structs.py - 165 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/resolvelib/compat/
  [LIB] __init__.py - 0 lines
  [LIB] collections_abc.py - 6 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/rich/
  [LIB] __init__.py - 172 lines
  [LIB] __main__.py - 280 lines
  [LIB] _cell_widths.py - 451 lines
  [LIB] _emoji_codes.py - 3610 lines
  [LIB] _emoji_replace.py - 32 lines
  [LIB] _extension.py - 10 lines
  [LIB] _inspect.py - 210 lines
  [LIB] _log_render.py - 94 lines
  [LIB] _loop.py - 43 lines
  [LIB] _lru_cache.py - 34 lines
  [LIB] _palettes.py - 309 lines
  [LIB] _pick.py - 17 lines
  [LIB] _ratio.py - 160 lines
  [LIB] _spinners.py - 848 lines
  [LIB] _stack.py - 16 lines
  [LIB] _timer.py - 19 lines
  [LIB] _windows.py - 72 lines
  [LIB] _wrap.py - 55 lines
  [LIB] abc.py - 33 lines
  [LIB] align.py - 312 lines
  [LIB] ansi.py - 228 lines
  [LIB] bar.py - 94 lines
  [LIB] box.py - 483 lines
  [LIB] cells.py - 147 lines
  [LIB] color.py - 581 lines
  [LIB] color_triplet.py - 38 lines
  [LIB] columns.py - 187 lines
  [LIB] console.py - 2211 lines
  [LIB] constrain.py - 37 lines
  [LIB] containers.py - 167 lines
  [LIB] control.py - 175 lines
  [LIB] default_styles.py - 183 lines
  [LIB] diagnose.py - 6 lines
  [LIB] emoji.py - 96 lines
  [LIB] errors.py - 34 lines
  [LIB] file_proxy.py - 54 lines
  [LIB] filesize.py - 89 lines
  [LIB] highlighter.py - 147 lines (ports: 7334)
  [LIB] json.py - 140 lines
  [LIB] jupyter.py - 92 lines
  [LIB] layout.py - 444 lines
  [LIB] live.py - 365 lines
  [LIB] live_render.py - 113 lines
  [LIB] logging.py - 268 lines (ports: 8080)
  [LIB] markup.py - 244 lines
  [LIB] measure.py - 149 lines
  [LIB] padding.py - 141 lines
  [LIB] pager.py - 34 lines
  [LIB] palette.py - 100 lines
  [LIB] panel.py - 250 lines
  [LIB] pretty.py - 903 lines
  [LIB] progress.py - 1036 lines
  [LIB] progress_bar.py - 216 lines
  [LIB] prompt.py - 376 lines
  [LIB] protocol.py - 42 lines
  [LIB] region.py - 10 lines
  [LIB] repr.py - 151 lines
  [LIB] rule.py - 115 lines
  [LIB] scope.py - 86 lines
  [LIB] screen.py - 54 lines
  [LIB] segment.py - 720 lines
  [LIB] spinner.py - 134 lines
  [LIB] status.py - 132 lines
  [LIB] style.py - 785 lines
  [LIB] styled.py - 42 lines
  [LIB] syntax.py - 735 lines
  [LIB] table.py - 968 lines
  [LIB] tabulate.py - 51 lines
  [LIB] terminal_theme.py - 55 lines
  [LIB] text.py - 1282 lines
  [LIB] theme.py - 112 lines
  [LIB] themes.py - 5 lines
  [LIB] traceback.py - 678 lines
  [LIB] tree.py - 249 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/tenacity/
  [LIB] __init__.py - 517 lines
  [LIB] _asyncio.py - 92 lines
  [LIB] _utils.py - 68 lines
  [LIB] after.py - 46 lines
  [LIB] before.py - 41 lines
  [LIB] before_sleep.py - 58 lines
  [LIB] nap.py - 43 lines
  [LIB] retry.py - 213 lines
  [LIB] stop.py - 96 lines
  [LIB] tornadoweb.py - 59 lines
  [LIB] wait.py - 191 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/tomli/
  [LIB] __init__.py - 6 lines
  [LIB] _parser.py - 703 lines
  [LIB] _re.py - 83 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/urllib3/
  [LIB] __init__.py - 85 lines
  [LIB] _collections.py - 355 lines
  [LIB] _version.py - 2 lines
  [LIB] connection.py - 569 lines
  [LIB] connectionpool.py - 1113 lines
  [LIB] exceptions.py - 323 lines (ports: 8080)
  [LIB] fields.py - 274 lines
  [LIB] filepost.py - 98 lines
  [LIB] poolmanager.py - 555 lines (ports: 3128)
  [LIB] request.py - 170 lines
  [LIB] response.py - 821 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/urllib3/contrib/
  [LIB] __init__.py - 0 lines
  [LIB] _appengine_environ.py - 36 lines
  [LIB] appengine.py - 314 lines
  [LIB] ntlmpool.py - 130 lines
  [LIB] pyopenssl.py - 511 lines
  [LIB] securetransport.py - 922 lines
  [LIB] socks.py - 216 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/urllib3/contrib/_securetransport/
  [LIB] __init__.py - 0 lines
  [LIB] bindings.py - 519 lines
  [LIB] low_level.py - 397 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/urllib3/packages/
  [LIB] __init__.py - 0 lines
  [LIB] six.py - 1077 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/urllib3/packages/backports/
  [LIB] __init__.py - 0 lines
  [LIB] makefile.py - 51 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/urllib3/util/
  [LIB] __init__.py - 49 lines
  [LIB] connection.py - 149 lines
  [LIB] proxy.py - 57 lines
  [LIB] queue.py - 22 lines
  [LIB] request.py - 143 lines
  [LIB] response.py - 107 lines
  [LIB] retry.py - 622 lines
  [LIB] ssl_.py - 495 lines
  [LIB] ssl_match_hostname.py - 161 lines
  [LIB] ssltransport.py - 221 lines
  [LIB] timeout.py - 268 lines
  [LIB] url.py - 432 lines
  [LIB] wait.py - 153 lines
ta-lib/venv/lib/python3.10/site-packages/pip/_vendor/webencodings/
  [LIB] __init__.py - 342 lines
  [LIB] labels.py - 231 lines (ports: 1987,1988,1989)
  [EXEC] mklabels.py - 59 lines
  [TEST] tests.py - 153 lines
  [LIB] x_user_defined.py - 325 lines
ta-lib/venv/lib/python3.10/site-packages/pkg_resources/
  [LIB] __init__.py - 3303 lines
ta-lib/venv/lib/python3.10/site-packages/pkg_resources/_vendor/
  [LIB] __init__.py - 0 lines
  [LIB] appdirs.py - 608 lines
  [LIB] pyparsing.py - 5742 lines
ta-lib/venv/lib/python3.10/site-packages/pkg_resources/_vendor/packaging/
  [LIB] __about__.py - 26 lines
  [LIB] __init__.py - 25 lines
  [LIB] _manylinux.py - 301 lines
  [LIB] _musllinux.py - 136 lines
  [LIB] _structures.py - 67 lines
  [LIB] markers.py - 304 lines
  [LIB] requirements.py - 146 lines
  [LIB] specifiers.py - 828 lines
  [LIB] tags.py - 484 lines
  [LIB] utils.py - 136 lines
  [LIB] version.py - 504 lines
ta-lib/venv/lib/python3.10/site-packages/pkg_resources/extern/
  [LIB] __init__.py - 73 lines
ta-lib/venv/lib/python3.10/site-packages/pkg_resources/tests/data/my-test-package-source/
  [LIB] setup.py - 6 lines
ta-lib/venv/lib/python3.10/site-packages/propcache/
  [LIB] __init__.py - 32 lines
  [LIB] _helpers.py - 39 lines
  [LIB] _helpers_py.py - 60 lines
  [LIB] api.py - 8 lines
ta-lib/venv/lib/python3.10/site-packages/pydantic/
  [LIB] __init__.py - 445 lines
  [LIB] _migration.py - 308 lines
  [LIB] alias_generators.py - 62 lines
  [LIB] aliases.py - 135 lines
  [LIB] annotated_handlers.py - 122 lines
  [LIB] class_validators.py - 5 lines
  [LIB] color.py - 604 lines
  [CONFIG] config.py - 1213 lines
  [LIB] dataclasses.py - 383 lines
  [LIB] datetime_parse.py - 5 lines
  [LIB] decorator.py - 5 lines
  [LIB] env_settings.py - 5 lines
  [LIB] error_wrappers.py - 5 lines
  [LIB] errors.py - 189 lines
  [LIB] fields.py - 1559 lines
  [LIB] functional_serializers.py - 450 lines
  [LIB] functional_validators.py - 828 lines
  [LIB] generics.py - 5 lines
  [LIB] json.py - 5 lines
  [LIB] json_schema.py - 2695 lines
  [LIB] main.py - 1773 lines
  [LIB] mypy.py - 1380 lines
  [LIB] networks.py - 1312 lines (ports: 3306,4222,5432,6379,8000,9000,9092,27017)
  [LIB] parse.py - 5 lines
  [LIB] root_model.py - 157 lines
  [LIB] schema.py - 5 lines
  [LIB] tools.py - 5 lines
  [LIB] type_adapter.py - 727 lines
  [LIB] types.py - 3285 lines
  [LIB] typing.py - 5 lines
  [LIB] utils.py - 5 lines
  [LIB] validate_call_decorator.py - 116 lines
  [LIB] validators.py - 5 lines
  [LIB] version.py - 84 lines
  [LIB] warnings.py - 96 lines
ta-lib/venv/lib/python3.10/site-packages/pydantic/_internal/
  [LIB] __init__.py - 0 lines
  [CONFIG] _config.py - 373 lines
  [LIB] _core_metadata.py - 97 lines
  [LIB] _core_utils.py - 182 lines
  [LIB] _dataclasses.py - 238 lines
  [LIB] _decorators.py - 838 lines
  [LIB] _decorators_v1.py - 174 lines
  [LIB] _discriminated_union.py - 479 lines
  [LIB] _docs_extraction.py - 108 lines
  [LIB] _fields.py - 515 lines
  [LIB] _forward_ref.py - 23 lines
  [LIB] _generate_schema.py - 2904 lines
  [LIB] _generics.py - 547 lines
  [LIB] _git.py - 27 lines
  [LIB] _import_utils.py - 20 lines
  [LIB] _internal_dataclass.py - 7 lines
  [LIB] _known_annotated_metadata.py - 393 lines
  [LIB] _mock_val_ser.py - 228 lines
  [LIB] _model_construction.py - 792 lines
  [LIB] _namespace_utils.py - 293 lines
  [LIB] _repr.py - 125 lines
  [LIB] _schema_gather.py - 209 lines
  [LIB] _schema_generation_shared.py - 125 lines
  [LIB] _serializers.py - 53 lines
  [LIB] _signature.py - 188 lines
  [LIB] _typing_extra.py - 714 lines
  [LIB] _utils.py - 431 lines
  [LIB] _validate_call.py - 140 lines
  [LIB] _validators.py - 532 lines
ta-lib/venv/lib/python3.10/site-packages/pydantic/deprecated/
  [LIB] __init__.py - 0 lines
  [LIB] class_validators.py - 256 lines
  [CONFIG] config.py - 72 lines
  [LIB] copy_internals.py - 224 lines
  [LIB] decorator.py - 284 lines
  [LIB] json.py - 141 lines
  [LIB] parse.py - 80 lines
  [LIB] tools.py - 103 lines
ta-lib/venv/lib/python3.10/site-packages/pydantic/experimental/
  [LIB] __init__.py - 10 lines
  [LIB] arguments_schema.py - 44 lines
  [LIB] pipeline.py - 667 lines
ta-lib/venv/lib/python3.10/site-packages/pydantic/plugin/
  [LIB] __init__.py - 188 lines
  [LIB] _loader.py - 57 lines
  [LIB] _schema_validator.py - 140 lines
ta-lib/venv/lib/python3.10/site-packages/pydantic/v1/
  [LIB] __init__.py - 131 lines
  [LIB] _hypothesis_plugin.py - 391 lines
  [LIB] annotated_types.py - 72 lines
  [LIB] class_validators.py - 361 lines
  [LIB] color.py - 494 lines
  [CONFIG] config.py - 191 lines
  [LIB] dataclasses.py - 500 lines
  [LIB] datetime_parse.py - 248 lines
  [LIB] decorator.py - 264 lines
  [LIB] env_settings.py - 350 lines
  [LIB] error_wrappers.py - 161 lines
  [LIB] errors.py - 646 lines
  [LIB] fields.py - 1253 lines
  [LIB] generics.py - 400 lines
  [LIB] json.py - 112 lines
  [LIB] main.py - 1113 lines
  [LIB] mypy.py - 949 lines
  [LIB] networks.py - 747 lines
  [LIB] parse.py - 66 lines
  [LIB] schema.py - 1163 lines
  [LIB] tools.py - 92 lines
  [LIB] types.py - 1205 lines
  [LIB] typing.py - 615 lines
  [LIB] utils.py - 806 lines
  [LIB] validators.py - 768 lines
  [LIB] version.py - 38 lines
ta-lib/venv/lib/python3.10/site-packages/pydantic_core/
  [LIB] __init__.py - 144 lines
  [LIB] core_schema.py - 4325 lines
ta-lib/venv/lib/python3.10/site-packages/pygments/
  [LIB] __init__.py - 82 lines
  [LIB] __main__.py - 17 lines
  [LIB] cmdline.py - 668 lines
  [LIB] console.py - 70 lines
  [LIB] filter.py - 70 lines
  [LIB] formatter.py - 129 lines
  [LIB] lexer.py - 961 lines (ports: 1024)
  [LIB] modeline.py - 43 lines
  [LIB] plugin.py - 72 lines
  [LIB] regexopt.py - 91 lines
  [LIB] scanner.py - 104 lines
  [LIB] sphinxext.py - 247 lines
  [LIB] style.py - 203 lines
  [LIB] token.py - 214 lines
  [EXEC] unistring.py - 153 lines
  [LIB] util.py - 324 lines
ta-lib/venv/lib/python3.10/site-packages/pygments/filters/
  [LIB] __init__.py - 940 lines
ta-lib/venv/lib/python3.10/site-packages/pygments/formatters/
  [LIB] __init__.py - 157 lines
  [LIB] _mapping.py - 23 lines
  [LIB] bbcode.py - 108 lines
  [LIB] groff.py - 170 lines
  [LIB] html.py - 995 lines
  [LIB] img.py - 686 lines
  [LIB] irc.py - 154 lines
  [LIB] latex.py - 518 lines
  [LIB] other.py - 160 lines
  [LIB] pangomarkup.py - 83 lines
  [LIB] rtf.py - 349 lines
  [LIB] svg.py - 185 lines
  [LIB] terminal.py - 127 lines
  [LIB] terminal256.py - 338 lines
ta-lib/venv/lib/python3.10/site-packages/pygments/lexers/
  [LIB] __init__.py - 362 lines
  [LIB] _ada_builtins.py - 103 lines
  [LIB] _asy_builtins.py - 1644 lines
  [LIB] _cl_builtins.py - 231 lines
  [EXEC] _cocoa_builtins.py - 75 lines
  [LIB] _csound_builtins.py - 1780 lines
  [LIB] _css_builtins.py - 558 lines
  [LIB] _googlesql_builtins.py - 918 lines
  [LIB] _julia_builtins.py - 411 lines
  [LIB] _lasso_builtins.py - 5326 lines
  [LIB] _lilypond_builtins.py - 4932 lines
  [EXEC] _lua_builtins.py - 285 lines
  [LIB] _luau_builtins.py - 62 lines
  [LIB] _mapping.py - 602 lines
  [LIB] _mql_builtins.py - 1171 lines
  [EXEC] _mysql_builtins.py - 1335 lines
  [LIB] _openedge_builtins.py - 2600 lines
  [EXEC] _php_builtins.py - 3325 lines
  [EXEC] _postgres_builtins.py - 739 lines
  [LIB] _qlik_builtins.py - 666 lines
  [LIB] _scheme_builtins.py - 1609 lines
  [EXEC] _scilab_builtins.py - 3093 lines
  [EXEC] _sourcemod_builtins.py - 1151 lines
  [LIB] _sql_builtins.py - 106 lines
  [LIB] _stan_builtins.py - 648 lines
  [LIB] _stata_builtins.py - 457 lines
  [LIB] _tsql_builtins.py - 1003 lines
  [LIB] _usd_builtins.py - 112 lines
  [LIB] _vbscript_builtins.py - 279 lines
  [LIB] _vim_builtins.py - 1938 lines
  [LIB] actionscript.py - 243 lines
  [LIB] ada.py - 144 lines
  [LIB] agile.py - 25 lines
  [LIB] algebra.py - 299 lines
  [LIB] ambient.py - 75 lines
  [LIB] amdgpu.py - 54 lines
  [LIB] ampl.py - 87 lines
  [LIB] apdlexer.py - 593 lines
  [LIB] apl.py - 103 lines
  [LIB] archetype.py - 315 lines
  [LIB] arrow.py - 116 lines
  [LIB] arturo.py - 249 lines
  [LIB] asc.py - 55 lines
  [LIB] asm.py - 1051 lines
  [LIB] asn1.py - 178 lines
  [LIB] automation.py - 379 lines
  [LIB] bare.py - 101 lines
  [LIB] basic.py - 656 lines
  [LIB] bdd.py - 57 lines
  [LIB] berry.py - 99 lines
  [LIB] bibtex.py - 159 lines
  [LIB] blueprint.py - 173 lines
  [LIB] boa.py - 97 lines
  [LIB] bqn.py - 112 lines
  [LIB] business.py - 625 lines
  [LIB] c_cpp.py - 414 lines
  [LIB] c_like.py - 738 lines
  [LIB] capnproto.py - 74 lines
  [LIB] carbon.py - 95 lines
  [LIB] cddl.py - 172 lines
  [LIB] chapel.py - 139 lines
  [LIB] clean.py - 180 lines
  [LIB] codeql.py - 80 lines
  [LIB] comal.py - 81 lines
  [LIB] compiled.py - 35 lines
  [CONFIG] configs.py - 1433 lines
  [LIB] console.py - 114 lines
  [LIB] cplint.py - 43 lines
  [LIB] crystal.py - 364 lines
  [LIB] csound.py - 466 lines
  [LIB] css.py - 602 lines
  [LIB] d.py - 259 lines
  [LIB] dalvik.py - 126 lines
  [LIB] data.py - 763 lines
  [LIB] dax.py - 135 lines
  [LIB] devicetree.py - 108 lines
  [LIB] diff.py - 169 lines
  [LIB] dns.py - 109 lines
  [LIB] dotnet.py - 873 lines
  [LIB] dsls.py - 970 lines
  [LIB] dylan.py - 279 lines
  [LIB] ecl.py - 144 lines
  [LIB] eiffel.py - 68 lines
  [LIB] elm.py - 123 lines
  [LIB] elpi.py - 175 lines
  [LIB] email.py - 132 lines
  [LIB] erlang.py - 526 lines
  [LIB] esoteric.py - 300 lines
  [LIB] ezhil.py - 76 lines
  [LIB] factor.py - 363 lines
  [LIB] fantom.py - 251 lines
  [LIB] felix.py - 275 lines
  [LIB] fift.py - 68 lines
  [LIB] floscript.py - 81 lines
  [LIB] forth.py - 178 lines
  [LIB] fortran.py - 212 lines
  [LIB] foxpro.py - 427 lines
  [LIB] freefem.py - 893 lines
  [LIB] func.py - 110 lines
  [LIB] functional.py - 21 lines
  [LIB] futhark.py - 105 lines
  [LIB] gcodelexer.py - 35 lines
  [LIB] gdscript.py - 189 lines
  [LIB] gleam.py - 74 lines
  [LIB] go.py - 97 lines
  [LIB] grammar_notation.py - 262 lines
  [LIB] graph.py - 108 lines
  [LIB] graphics.py - 794 lines
  [LIB] graphql.py - 176 lines
  [LIB] graphviz.py - 58 lines
  [LIB] gsql.py - 103 lines
  [LIB] hare.py - 73 lines
  [LIB] haskell.py - 866 lines
  [LIB] haxe.py - 935 lines
  [LIB] hdl.py - 466 lines
  [LIB] hexdump.py - 102 lines
  [LIB] html.py - 670 lines
  [LIB] idl.py - 284 lines
  [LIB] igor.py - 435 lines
  [LIB] inferno.py - 95 lines
  [LIB] installers.py - 352 lines
  [LIB] int_fiction.py - 1370 lines
  [LIB] iolang.py - 61 lines
  [LIB] j.py - 151 lines
  [LIB] javascript.py - 1591 lines
  [LIB] jmespath.py - 69 lines
  [LIB] jslt.py - 94 lines
  [LIB] json5.py - 83 lines
  [LIB] jsonnet.py - 169 lines
  [LIB] jsx.py - 100 lines
  [LIB] julia.py - 294 lines
  [LIB] jvm.py - 1802 lines
  [LIB] kuin.py - 332 lines
  [LIB] kusto.py - 93 lines
  [LIB] ldap.py - 155 lines
  [LIB] lean.py - 241 lines
  [LIB] lilypond.py - 225 lines
  [LIB] lisp.py - 3146 lines
  [LIB] macaulay2.py - 1814 lines
  [LIB] make.py - 212 lines
  [LIB] maple.py - 291 lines
  [LIB] markup.py - 1654 lines
  [LIB] math.py - 21 lines
  [LIB] matlab.py - 3307 lines
  [LIB] maxima.py - 84 lines
  [LIB] meson.py - 139 lines
  [LIB] mime.py - 210 lines
  [LIB] minecraft.py - 391 lines
  [LIB] mips.py - 130 lines
  [LIB] ml.py - 958 lines
  [LIB] modeling.py - 366 lines
  [LIB] modula2.py - 1579 lines
  [LIB] mojo.py - 707 lines
  [LIB] monte.py - 203 lines
  [LIB] mosel.py - 447 lines
  [LIB] ncl.py - 894 lines
  [LIB] nimrod.py - 199 lines
  [LIB] nit.py - 63 lines
  [LIB] nix.py - 144 lines
  [LIB] numbair.py - 63 lines
  [LIB] oberon.py - 120 lines
  [LIB] objective.py - 513 lines
  [LIB] ooc.py - 84 lines
  [LIB] openscad.py - 96 lines
  [LIB] other.py - 41 lines
  [LIB] parasail.py - 78 lines
  [LIB] parsers.py - 798 lines
  [LIB] pascal.py - 644 lines
  [LIB] pawn.py - 202 lines
  [LIB] pddl.py - 82 lines
  [LIB] perl.py - 733 lines
  [LIB] phix.py - 363 lines
  [LIB] php.py - 334 lines
  [LIB] pointless.py - 70 lines
  [LIB] pony.py - 93 lines
  [LIB] praat.py - 303 lines
  [LIB] procfile.py - 41 lines
  [LIB] prolog.py - 318 lines
  [LIB] promql.py - 176 lines
  [LIB] prql.py - 251 lines
  [LIB] ptx.py - 119 lines
  [LIB] python.py - 1201 lines
  [LIB] q.py - 187 lines
  [LIB] qlik.py - 117 lines
  [LIB] qvt.py - 153 lines
  [LIB] r.py - 196 lines
  [LIB] rdf.py - 468 lines
  [LIB] rebol.py - 419 lines
  [LIB] rego.py - 57 lines
  [LIB] resource.py - 83 lines
  [LIB] ride.py - 138 lines
  [LIB] rita.py - 42 lines
  [LIB] rnc.py - 66 lines
  [LIB] roboconf.py - 81 lines
  [LIB] robotframework.py - 551 lines
  [LIB] ruby.py - 518 lines
  [LIB] rust.py - 222 lines
  [LIB] sas.py - 227 lines
  [LIB] savi.py - 171 lines
  [LIB] scdoc.py - 85 lines
  [LIB] scripting.py - 1616 lines
  [LIB] sgf.py - 59 lines
  [LIB] shell.py - 902 lines
  [LIB] sieve.py - 78 lines
  [LIB] slash.py - 183 lines
  [LIB] smalltalk.py - 194 lines
  [LIB] smithy.py - 77 lines
  [LIB] smv.py - 78 lines
  [LIB] snobol.py - 82 lines
  [LIB] solidity.py - 87 lines
  [LIB] soong.py - 78 lines
  [LIB] sophia.py - 102 lines
  [LIB] special.py - 122 lines
  [LIB] spice.py - 70 lines
  [LIB] sql.py - 1109 lines
  [LIB] srcinfo.py - 62 lines
  [LIB] stata.py - 170 lines
  [LIB] supercollider.py - 94 lines
  [LIB] tablegen.py - 177 lines
  [LIB] tact.py - 303 lines
  [LIB] tal.py - 77 lines
  [LIB] tcl.py - 148 lines
  [LIB] teal.py - 88 lines
  [LIB] templates.py - 2355 lines
  [LIB] teraterm.py - 325 lines
  [TEST] testing.py - 209 lines
  [LIB] text.py - 27 lines
  [LIB] textedit.py - 205 lines
  [LIB] textfmts.py - 436 lines
  [LIB] theorem.py - 410 lines
  [LIB] thingsdb.py - 140 lines
  [LIB] tlb.py - 59 lines
  [LIB] tls.py - 54 lines
  [LIB] tnt.py - 270 lines
  [LIB] trafficscript.py - 51 lines
  [LIB] typoscript.py - 216 lines
  [LIB] typst.py - 160 lines
  [LIB] ul4.py - 309 lines
  [LIB] unicon.py - 413 lines
  [LIB] urbi.py - 145 lines
  [LIB] usd.py - 85 lines
  [LIB] varnish.py - 189 lines
  [LIB] verification.py - 113 lines
  [LIB] verifpal.py - 65 lines
  [LIB] vip.py - 150 lines
  [LIB] vyper.py - 140 lines
  [LIB] web.py - 24 lines
  [LIB] webassembly.py - 119 lines
  [LIB] webidl.py - 298 lines
  [LIB] webmisc.py - 1006 lines
  [LIB] wgsl.py - 406 lines
  [LIB] whiley.py - 115 lines
  [LIB] wowtoc.py - 120 lines
  [LIB] wren.py - 98 lines
  [LIB] x10.py - 66 lines
  [LIB] xorg.py - 38 lines
  [LIB] yang.py - 103 lines
  [LIB] yara.py - 69 lines
  [LIB] zig.py - 125 lines
ta-lib/venv/lib/python3.10/site-packages/pygments/styles/
  [LIB] __init__.py - 61 lines
  [LIB] _mapping.py - 54 lines
  [LIB] abap.py - 32 lines
  [LIB] algol.py - 65 lines
  [LIB] algol_nu.py - 65 lines
  [LIB] arduino.py - 100 lines
  [LIB] autumn.py - 67 lines
  [LIB] borland.py - 53 lines
  [LIB] bw.py - 52 lines
  [LIB] coffee.py - 80 lines
  [LIB] colorful.py - 83 lines
  [LIB] default.py - 76 lines
  [LIB] dracula.py - 90 lines
  [LIB] emacs.py - 75 lines
  [LIB] friendly.py - 76 lines
  [LIB] friendly_grayscale.py - 80 lines
  [LIB] fruity.py - 47 lines
  [LIB] gh_dark.py - 113 lines
  [LIB] gruvbox.py - 118 lines
  [LIB] igor.py - 32 lines
  [LIB] inkpot.py - 72 lines
  [LIB] lightbulb.py - 110 lines
  [LIB] lilypond.py - 62 lines
  [LIB] lovelace.py - 100 lines
  [LIB] manni.py - 79 lines
  [LIB] material.py - 124 lines
  [LIB] monokai.py - 112 lines
  [LIB] murphy.py - 82 lines
  [LIB] native.py - 70 lines
  [LIB] nord.py - 156 lines
  [LIB] onedark.py - 63 lines
  [LIB] paraiso_dark.py - 124 lines
  [LIB] paraiso_light.py - 124 lines
  [LIB] pastie.py - 78 lines
  [LIB] perldoc.py - 73 lines
  [LIB] rainbow_dash.py - 95 lines
  [LIB] rrt.py - 40 lines
  [LIB] sas.py - 46 lines
  [LIB] solarized.py - 144 lines
  [LIB] staroffice.py - 31 lines
  [LIB] stata_dark.py - 42 lines
  [LIB] stata_light.py - 42 lines
  [LIB] tango.py - 143 lines
  [LIB] trac.py - 66 lines
  [LIB] vim.py - 67 lines
  [LIB] vs.py - 41 lines
  [LIB] xcode.py - 53 lines
  [LIB] zenburn.py - 83 lines
ta-lib/venv/lib/python3.10/site-packages/pytz/
  [EXEC] __init__.py - 1556 lines
  [LIB] exceptions.py - 59 lines
  [LIB] lazy.py - 172 lines
  [LIB] reference.py - 140 lines
  [EXEC] tzfile.py - 133 lines
  [LIB] tzinfo.py - 580 lines
ta-lib/venv/lib/python3.10/site-packages/rich/
  [LIB] __init__.py - 177 lines
  [LIB] __main__.py - 273 lines
  [LIB] _cell_widths.py - 454 lines
  [LIB] _emoji_codes.py - 3610 lines
  [LIB] _emoji_replace.py - 32 lines
  [LIB] _export_format.py - 76 lines
  [LIB] _extension.py - 10 lines
  [LIB] _fileno.py - 24 lines
  [LIB] _inspect.py - 268 lines
  [LIB] _log_render.py - 94 lines
  [LIB] _loop.py - 43 lines
  [LIB] _null_file.py - 69 lines
  [LIB] _palettes.py - 309 lines
  [LIB] _pick.py - 17 lines
  [LIB] _ratio.py - 159 lines
  [LIB] _spinners.py - 482 lines
  [LIB] _stack.py - 16 lines
  [LIB] _timer.py - 19 lines
  [LIB] _win32_console.py - 661 lines
  [LIB] _windows.py - 71 lines
  [LIB] _windows_renderer.py - 56 lines
  [LIB] _wrap.py - 93 lines
  [LIB] abc.py - 33 lines
  [LIB] align.py - 312 lines
  [LIB] ansi.py - 241 lines
  [LIB] bar.py - 93 lines
  [LIB] box.py - 480 lines
  [LIB] cells.py - 174 lines
  [LIB] color.py - 621 lines
  [LIB] color_triplet.py - 38 lines
  [LIB] columns.py - 187 lines
  [LIB] console.py - 2675 lines
  [LIB] constrain.py - 37 lines
  [LIB] containers.py - 167 lines
  [LIB] control.py - 225 lines
  [LIB] default_styles.py - 193 lines
  [LIB] diagnose.py - 38 lines
  [LIB] emoji.py - 96 lines
  [LIB] errors.py - 34 lines
  [LIB] file_proxy.py - 57 lines
  [LIB] filesize.py - 88 lines
  [LIB] highlighter.py - 232 lines (ports: 7334)
  [LIB] json.py - 139 lines
  [LIB] jupyter.py - 101 lines
  [LIB] layout.py - 442 lines
  [LIB] live.py - 375 lines
  [LIB] live_render.py - 112 lines
  [LIB] logging.py - 297 lines (ports: 8080)
  [LIB] markdown.py - 784 lines
  [LIB] markup.py - 251 lines
  [LIB] measure.py - 151 lines
  [LIB] padding.py - 141 lines
  [LIB] pager.py - 34 lines
  [LIB] palette.py - 100 lines
  [LIB] panel.py - 318 lines
  [LIB] pretty.py - 1016 lines
  [LIB] progress.py - 1715 lines
  [LIB] progress_bar.py - 223 lines
  [LIB] prompt.py - 400 lines
  [LIB] protocol.py - 42 lines
  [LIB] region.py - 10 lines
  [LIB] repr.py - 149 lines
  [LIB] rule.py - 130 lines
  [LIB] scope.py - 86 lines
  [LIB] screen.py - 54 lines
  [LIB] segment.py - 752 lines
  [LIB] spinner.py - 138 lines
  [LIB] status.py - 131 lines
  [LIB] style.py - 796 lines
  [LIB] styled.py - 42 lines
  [LIB] syntax.py - 966 lines
  [LIB] table.py - 1006 lines
  [LIB] terminal_theme.py - 153 lines
  [LIB] text.py - 1361 lines
  [LIB] theme.py - 115 lines
  [LIB] themes.py - 5 lines
  [LIB] traceback.py - 884 lines
  [LIB] tree.py - 257 lines
ta-lib/venv/lib/python3.10/site-packages/setuptools/
  [LIB] __init__.py - 242 lines
  [LIB] _deprecation_warning.py - 7 lines
  [LIB] _imp.py - 82 lines
  [LIB] archive_util.py - 205 lines
  [LIB] build_meta.py - 290 lines
  [CONFIG] config.py - 751 lines
  [LIB] dep_util.py - 25 lines
  [LIB] depends.py - 176 lines
  [LIB] dist.py - 1156 lines
  [LIB] errors.py - 40 lines
  [LIB] extension.py - 55 lines
  [LIB] glob.py - 167 lines
  [LIB] installer.py - 104 lines
  [EXEC] launch.py - 36 lines
  [LIB] monkey.py - 177 lines
  [LIB] msvc.py - 1805 lines
  [LIB] namespaces.py - 107 lines
  [LIB] package_index.py - 1176 lines
  [LIB] py34compat.py - 13 lines
  [LIB] sandbox.py - 530 lines
  [LIB] unicode_utils.py - 42 lines
  [LIB] version.py - 6 lines
  [LIB] wheel.py - 213 lines
  [LIB] windows_support.py - 29 lines
ta-lib/venv/lib/python3.10/site-packages/setuptools/_distutils/
  [LIB] __init__.py - 24 lines
  [LIB] _msvccompiler.py - 561 lines
  [LIB] archive_util.py - 256 lines
  [LIB] bcppcompiler.py - 393 lines
  [LIB] ccompiler.py - 1123 lines
  [LIB] cmd.py - 403 lines
  [CONFIG] config.py - 130 lines
  [LIB] core.py - 249 lines
  [LIB] cygwinccompiler.py - 425 lines
  [LIB] debug.py - 5 lines
  [LIB] dep_util.py - 92 lines
  [LIB] dir_util.py - 210 lines
  [LIB] dist.py - 1257 lines
  [LIB] errors.py - 97 lines
  [LIB] extension.py - 240 lines
  [LIB] fancy_getopt.py - 457 lines
  [LIB] file_util.py - 238 lines
  [LIB] filelist.py - 355 lines
  [LIB] log.py - 77 lines
  [LIB] msvc9compiler.py - 788 lines
  [LIB] msvccompiler.py - 643 lines
  [LIB] py35compat.py - 19 lines
  [LIB] py38compat.py - 7 lines
  [LIB] spawn.py - 106 lines
  [CONFIG] sysconfig.py - 601 lines
  [LIB] text_file.py - 286 lines
  [LIB] unixccompiler.py - 325 lines
  [LIB] util.py - 548 lines
  [LIB] version.py - 363 lines
  [LIB] versionpredicate.py - 169 lines
ta-lib/venv/lib/python3.10/site-packages/setuptools/_distutils/command/
  [LIB] __init__.py - 31 lines
  [LIB] bdist.py - 143 lines
  [LIB] bdist_dumb.py - 123 lines
  [LIB] bdist_msi.py - 749 lines
  [LIB] bdist_rpm.py - 579 lines
  [LIB] bdist_wininst.py - 377 lines
  [LIB] build.py - 157 lines
  [LIB] build_clib.py - 209 lines
  [LIB] build_ext.py - 755 lines
  [LIB] build_py.py - 392 lines
  [LIB] build_scripts.py - 152 lines
  [LIB] check.py - 148 lines
  [LIB] clean.py - 76 lines
  [CONFIG] config.py - 344 lines
  [LIB] install.py - 721 lines
  [LIB] install_data.py - 79 lines
  [LIB] install_egg_info.py - 84 lines
  [LIB] install_headers.py - 47 lines
  [LIB] install_lib.py - 217 lines
  [LIB] install_scripts.py - 60 lines
  [LIB] py37compat.py - 30 lines
  [LIB] register.py - 304 lines
  [LIB] sdist.py - 494 lines
  [LIB] upload.py - 214 lines
ta-lib/venv/lib/python3.10/site-packages/setuptools/_vendor/
  [LIB] __init__.py - 0 lines
  [LIB] ordered_set.py - 488 lines
  [LIB] pyparsing.py - 5742 lines
ta-lib/venv/lib/python3.10/site-packages/setuptools/_vendor/more_itertools/
  [LIB] __init__.py - 4 lines
  [LIB] more.py - 3825 lines
  [LIB] recipes.py - 620 lines
ta-lib/venv/lib/python3.10/site-packages/setuptools/_vendor/packaging/
  [LIB] __about__.py - 26 lines
  [LIB] __init__.py - 25 lines
  [LIB] _manylinux.py - 301 lines
  [LIB] _musllinux.py - 136 lines
  [LIB] _structures.py - 67 lines
  [LIB] markers.py - 304 lines
  [LIB] requirements.py - 146 lines
  [LIB] specifiers.py - 828 lines
  [LIB] tags.py - 484 lines
  [LIB] utils.py - 136 lines
  [LIB] version.py - 504 lines
ta-lib/venv/lib/python3.10/site-packages/setuptools/command/
  [LIB] __init__.py - 8 lines
  [LIB] alias.py - 78 lines
  [LIB] bdist_egg.py - 456 lines
  [LIB] bdist_rpm.py - 40 lines
  [LIB] build_clib.py - 101 lines
  [LIB] build_ext.py - 328 lines
  [LIB] build_py.py - 242 lines
  [LIB] develop.py - 193 lines
  [LIB] dist_info.py - 36 lines
  [EXEC] easy_install.py - 2354 lines
  [LIB] egg_info.py - 755 lines
  [LIB] install.py - 132 lines
  [LIB] install_egg_info.py - 82 lines
  [LIB] install_lib.py - 148 lines
  [LIB] install_scripts.py - 69 lines
  [LIB] py36compat.py - 134 lines
  [LIB] register.py - 18 lines
  [LIB] rotate.py - 64 lines
  [LIB] saveopts.py - 22 lines
  [LIB] sdist.py - 196 lines
  [LIB] setopt.py - 149 lines
  [TEST] test.py - 252 lines
  [LIB] upload.py - 17 lines
  [LIB] upload_docs.py - 202 lines
ta-lib/venv/lib/python3.10/site-packages/setuptools/extern/
  [LIB] __init__.py - 73 lines
ta-lib/venv/lib/python3.10/site-packages/sniffio/
  [LIB] __init__.py - 17 lines
  [LIB] _impl.py - 95 lines
  [LIB] _version.py - 3 lines
ta-lib/venv/lib/python3.10/site-packages/sniffio/_tests/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/starlette/
  [LIB] __init__.py - 1 lines
  [LIB] _exception_handler.py - 65 lines
  [LIB] _utils.py - 101 lines
  [LIB] applications.py - 250 lines
  [LIB] authentication.py - 148 lines
  [LIB] background.py - 42 lines
  [LIB] concurrency.py - 63 lines
  [CONFIG] config.py - 139 lines
  [LIB] convertors.py - 89 lines
  [LIB] datastructures.py - 692 lines
  [LIB] endpoints.py - 123 lines
  [LIB] exceptions.py - 33 lines
  [LIB] formparsers.py - 276 lines
  [LIB] requests.py - 323 lines
  [LIB] responses.py - 548 lines
  [LIB] routing.py - 876 lines
  [LIB] schemas.py - 147 lines
  [LIB] staticfiles.py - 220 lines
  [LIB] status.py - 95 lines
  [LIB] templating.py - 217 lines
  [TEST] testclient.py - 745 lines
  [LIB] types.py - 26 lines
  [LIB] websockets.py - 196 lines
ta-lib/venv/lib/python3.10/site-packages/starlette/middleware/
  [LIB] __init__.py - 42 lines
  [LIB] authentication.py - 52 lines
  [LIB] base.py - 235 lines
  [LIB] cors.py - 172 lines
  [LIB] errors.py - 259 lines
  [LIB] exceptions.py - 73 lines
  [LIB] gzip.py - 145 lines
  [LIB] httpsredirect.py - 19 lines
  [LIB] sessions.py - 85 lines
  [LIB] trustedhost.py - 60 lines
  [LIB] wsgi.py - 153 lines
ta-lib/venv/lib/python3.10/site-packages/typing_inspection/
  [LIB] __init__.py - 0 lines
  [LIB] introspection.py - 587 lines
  [LIB] typing_objects.py - 596 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/
  [LIB] __init__.py - 6 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Africa/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/America/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/America/Argentina/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/America/Indiana/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/America/Kentucky/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/America/North_Dakota/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Antarctica/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Arctic/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Asia/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Atlantic/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Australia/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Brazil/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Canada/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Chile/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Etc/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Europe/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Indian/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Mexico/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/Pacific/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/tzdata/zoneinfo/US/
  [LIB] __init__.py - 0 lines
ta-lib/venv/lib/python3.10/site-packages/uvicorn/
  [LIB] __init__.py - 5 lines
  [LIB] __main__.py - 4 lines
  [LIB] _subprocess.py - 84 lines
  [LIB] _types.py - 281 lines
  [CONFIG] config.py - 531 lines
  [LIB] importer.py - 34 lines
  [LIB] logging.py - 117 lines
  [LIB] main.py - 604 lines
  [SVC] server.py - 338 lines
  [LIB] workers.py - 114 lines
ta-lib/venv/lib/python3.10/site-packages/uvicorn/lifespan/
  [LIB] __init__.py - 0 lines
  [LIB] off.py - 17 lines
  [LIB] on.py - 137 lines
ta-lib/venv/lib/python3.10/site-packages/uvicorn/loops/
  [LIB] __init__.py - 0 lines
  [LIB] asyncio.py - 10 lines
  [LIB] auto.py - 11 lines
  [LIB] uvloop.py - 7 lines
ta-lib/venv/lib/python3.10/site-packages/uvicorn/middleware/
  [LIB] __init__.py - 0 lines
  [LIB] asgi2.py - 15 lines
  [LIB] message_logger.py - 87 lines
  [LIB] proxy_headers.py - 142 lines
  [LIB] wsgi.py - 199 lines
ta-lib/venv/lib/python3.10/site-packages/uvicorn/protocols/
  [LIB] __init__.py - 0 lines
  [LIB] utils.py - 56 lines
ta-lib/venv/lib/python3.10/site-packages/uvicorn/protocols/http/
  [LIB] __init__.py - 0 lines
  [LIB] auto.py - 15 lines
  [LIB] flow_control.py - 54 lines
  [LIB] h11_impl.py - 543 lines
  [LIB] httptools_impl.py - 570 lines
ta-lib/venv/lib/python3.10/site-packages/uvicorn/protocols/websockets/
  [LIB] __init__.py - 0 lines
  [LIB] auto.py - 21 lines
  [LIB] websockets_impl.py - 387 lines
  [LIB] websockets_sansio_impl.py - 417 lines
  [LIB] wsproto_impl.py - 377 lines
ta-lib/venv/lib/python3.10/site-packages/uvicorn/supervisors/
  [LIB] __init__.py - 16 lines
  [LIB] basereload.py - 126 lines
  [LIB] multiprocess.py - 222 lines
  [LIB] statreload.py - 53 lines
  [LIB] watchfilesreload.py - 85 lines
ta-lib/venv/lib/python3.10/site-packages/websockets/
  [LIB] __init__.py - 236 lines
  [LIB] __main__.py - 5 lines
  [LIB] auth.py - 18 lines
  [LIB] cli.py - 178 lines
  [LIB] client.py - 389 lines
  [LIB] connection.py - 12 lines
  [LIB] datastructures.py - 187 lines
  [LIB] exceptions.py - 473 lines
  [LIB] frames.py - 430 lines
  [LIB] headers.py - 586 lines
  [LIB] http.py - 20 lines
  [LIB] http11.py - 427 lines
  [LIB] imports.py - 100 lines
  [LIB] protocol.py - 758 lines
  [SVC] server.py - 587 lines
  [LIB] streams.py - 151 lines
  [LIB] typing.py - 74 lines
  [LIB] uri.py - 225 lines
  [LIB] utils.py - 51 lines
  [LIB] version.py - 92 lines
ta-lib/venv/lib/python3.10/site-packages/websockets/asyncio/
  [LIB] __init__.py - 0 lines
  [LIB] async_timeout.py - 282 lines
  [LIB] client.py - 820 lines
  [LIB] compatibility.py - 30 lines
  [LIB] connection.py - 1237 lines
  [LIB] messages.py - 314 lines
  [LIB] router.py - 198 lines
  [SVC] server.py - 981 lines
ta-lib/venv/lib/python3.10/site-packages/websockets/extensions/
  [LIB] __init__.py - 4 lines
  [LIB] base.py - 123 lines
  [LIB] permessage_deflate.py - 697 lines
ta-lib/venv/lib/python3.10/site-packages/websockets/legacy/
  [LIB] __init__.py - 11 lines
  [LIB] auth.py - 190 lines
  [LIB] client.py - 705 lines
  [LIB] exceptions.py - 71 lines
  [LIB] framing.py - 225 lines
  [LIB] handshake.py - 158 lines
  [LIB] http.py - 201 lines
  [LIB] protocol.py - 1641 lines
  [SVC] server.py - 1191 lines
ta-lib/venv/lib/python3.10/site-packages/websockets/sync/
  [LIB] __init__.py - 0 lines
  [LIB] client.py - 648 lines
  [LIB] connection.py - 1072 lines
  [LIB] messages.py - 345 lines
  [LIB] router.py - 192 lines
  [SVC] server.py - 763 lines
  [LIB] utils.py - 45 lines
ta-lib/venv/lib/python3.10/site-packages/yaml/
  [LIB] __init__.py - 390 lines
  [LIB] composer.py - 139 lines
  [LIB] constructor.py - 748 lines
  [LIB] cyaml.py - 101 lines
  [LIB] dumper.py - 62 lines
  [LIB] emitter.py - 1137 lines
  [LIB] error.py - 75 lines
  [LIB] events.py - 86 lines
  [LIB] loader.py - 63 lines
  [LIB] nodes.py - 49 lines
  [LIB] parser.py - 589 lines
  [LIB] reader.py - 185 lines
  [LIB] representer.py - 389 lines
  [LIB] resolver.py - 227 lines
  [LIB] scanner.py - 1435 lines
  [LIB] serializer.py - 111 lines
  [LIB] tokens.py - 104 lines
ta-lib/venv/lib/python3.10/site-packages/yarl/
  [LIB] __init__.py - 14 lines
  [LIB] _parse.py - 203 lines
  [LIB] _path.py - 41 lines
  [LIB] _query.py - 114 lines
  [LIB] _quoters.py - 33 lines
  [LIB] _quoting.py - 19 lines
  [LIB] _quoting_py.py - 213 lines
  [LIB] _url.py - 1604 lines (ports: 8080,8329,8443)
tests/
  [LIB] __init__.py - 0 lines
  [TEST] conftest.py - 94 lines (ports: 6379)
venv/lib/python3.10/site-packages/
  [LIB] decouple.py - 316 lines
  [LIB] six.py - 1003 lines
  [LIB] threadpoolctl.py - 1292 lines
  [LIB] typing_extensions.py - 4244 lines
venv/lib/python3.10/site-packages/_distutils_hack/
  [LIB] __init__.py - 132 lines
  [LIB] override.py - 1 lines
venv/lib/python3.10/site-packages/_yaml/
  [LIB] __init__.py - 33 lines
venv/lib/python3.10/site-packages/aiohappyeyeballs/
  [LIB] __init__.py - 14 lines
  [LIB] _staggered.py - 207 lines
  [LIB] impl.py - 259 lines
  [LIB] types.py - 17 lines
  [LIB] utils.py - 97 lines
venv/lib/python3.10/site-packages/aiohttp/
  [LIB] __init__.py - 278 lines
  [LIB] _cookie_helpers.py - 309 lines
  [LIB] abc.py - 268 lines
  [LIB] base_protocol.py - 100 lines
  [LIB] client.py - 1613 lines
  [LIB] client_exceptions.py - 421 lines
  [LIB] client_middleware_digest_auth.py - 474 lines
  [LIB] client_middlewares.py - 55 lines
  [LIB] client_proto.py - 359 lines
  [LIB] client_reqrep.py - 1533 lines
  [LIB] client_ws.py - 428 lines
  [LIB] compression_utils.py - 278 lines
  [LIB] connector.py - 1834 lines
  [LIB] cookiejar.py - 522 lines
  [LIB] formdata.py - 179 lines
  [LIB] hdrs.py - 121 lines
  [LIB] helpers.py - 958 lines
  [LIB] http.py - 72 lines
  [LIB] http_exceptions.py - 112 lines
  [LIB] http_parser.py - 1050 lines
  [LIB] http_websocket.py - 36 lines
  [LIB] http_writer.py - 378 lines
  [LIB] log.py - 8 lines
  [LIB] multipart.py - 1140 lines
  [LIB] payload.py - 1124 lines
  [LIB] payload_streamer.py - 78 lines
  [TEST] pytest_plugin.py - 444 lines
  [LIB] resolver.py - 274 lines
  [LIB] streams.py - 727 lines
  [LIB] tcp_helpers.py - 37 lines
  [LIB] tracing.py - 455 lines
  [LIB] typedefs.py - 69 lines
  [LIB] web.py - 605 lines
  [LIB] web_app.py - 620 lines
  [LIB] web_exceptions.py - 452 lines
  [LIB] web_fileresponse.py - 418 lines
  [LIB] web_log.py - 216 lines
  [LIB] web_middlewares.py - 121 lines
  [LIB] web_protocol.py - 792 lines
  [LIB] web_request.py - 916 lines (ports: 8080)
  [LIB] web_response.py - 856 lines
  [LIB] web_routedef.py - 214 lines
  [LIB] web_runner.py - 399 lines (ports: 8443)
  [SVC] web_server.py - 84 lines
  [LIB] web_urldispatcher.py - 1303 lines
  [LIB] web_ws.py - 631 lines
  [LIB] worker.py - 255 lines
venv/lib/python3.10/site-packages/aiohttp/_websocket/
  [LIB] __init__.py - 1 lines
  [LIB] helpers.py - 147 lines
  [LIB] models.py - 84 lines
  [LIB] reader.py - 31 lines
  [LIB] reader_c.py - 476 lines
  [LIB] reader_py.py - 476 lines
  [LIB] writer.py - 178 lines
venv/lib/python3.10/site-packages/aiosignal/
  [LIB] __init__.py - 59 lines
venv/lib/python3.10/site-packages/aiosqlite/
  [LIB] __init__.py - 44 lines
  [LIB] __version__.py - 7 lines
  [LIB] context.py - 56 lines
  [LIB] core.py - 384 lines
  [LIB] cursor.py - 110 lines
venv/lib/python3.10/site-packages/aiosqlite/tests/
  [LIB] __init__.py - 4 lines
  [LIB] __main__.py - 7 lines
  [LIB] helpers.py - 29 lines
  [LIB] perf.py - 203 lines
  [LIB] smoke.py - 464 lines
venv/lib/python3.10/site-packages/alembic/
  [LIB] __init__.py - 4 lines
  [LIB] __main__.py - 4 lines
  [LIB] command.py - 835 lines
  [CONFIG] config.py - 1020 lines
  [LIB] context.py - 5 lines
  [LIB] environment.py - 1 lines
  [LIB] migration.py - 1 lines
  [LIB] op.py - 5 lines
venv/lib/python3.10/site-packages/alembic/autogenerate/
  [LIB] __init__.py - 10 lines
  [LIB] api.py - 650 lines
  [LIB] compare.py - 1370 lines
  [LIB] render.py - 1172 lines
  [LIB] rewriter.py - 240 lines
venv/lib/python3.10/site-packages/alembic/ddl/
  [LIB] __init__.py - 6 lines
  [LIB] _autogen.py - 329 lines
  [LIB] base.py - 364 lines
  [LIB] impl.py - 902 lines
  [LIB] mssql.py - 421 lines
  [LIB] mysql.py - 495 lines
  [LIB] oracle.py - 202 lines
  [LIB] postgresql.py - 854 lines
  [LIB] sqlite.py - 237 lines
venv/lib/python3.10/site-packages/alembic/operations/
  [LIB] __init__.py - 15 lines
  [LIB] base.py - 1923 lines
  [LIB] batch.py - 718 lines
  [LIB] ops.py - 2842 lines
  [LIB] schemaobj.py - 290 lines
  [LIB] toimpl.py - 242 lines
venv/lib/python3.10/site-packages/alembic/runtime/
  [LIB] __init__.py - 0 lines
  [LIB] environment.py - 1051 lines
  [LIB] migration.py - 1395 lines
venv/lib/python3.10/site-packages/alembic/script/
  [LIB] __init__.py - 4 lines
  [LIB] base.py - 1055 lines
  [LIB] revision.py - 1728 lines
  [LIB] write_hooks.py - 176 lines
venv/lib/python3.10/site-packages/alembic/templates/async/
  [LIB] env.py - 89 lines
venv/lib/python3.10/site-packages/alembic/templates/generic/
  [LIB] env.py - 78 lines
venv/lib/python3.10/site-packages/alembic/templates/multidb/
  [LIB] env.py - 140 lines
venv/lib/python3.10/site-packages/alembic/templates/pyproject/
  [LIB] env.py - 78 lines
venv/lib/python3.10/site-packages/alembic/templates/pyproject_async/
  [LIB] env.py - 89 lines
venv/lib/python3.10/site-packages/alembic/testing/
  [LIB] __init__.py - 32 lines
  [LIB] assertions.py - 179 lines
  [LIB] env.py - 557 lines
  [LIB] fixtures.py - 333 lines
  [LIB] requirements.py - 176 lines
  [LIB] schemacompare.py - 169 lines
  [LIB] util.py - 126 lines
  [LIB] warnings.py - 31 lines
venv/lib/python3.10/site-packages/alembic/testing/plugin/
  [LIB] __init__.py - 0 lines
  [LIB] bootstrap.py - 4 lines
venv/lib/python3.10/site-packages/alembic/testing/suite/
  [LIB] __init__.py - 7 lines
  [LIB] _autogen_fixtures.py - 448 lines
venv/lib/python3.10/site-packages/alembic/util/
  [LIB] __init__.py - 29 lines
  [LIB] compat.py - 146 lines
  [LIB] editor.py - 81 lines
  [LIB] exc.py - 25 lines
  [LIB] langhelpers.py - 332 lines
  [LIB] messaging.py - 122 lines
  [LIB] pyfiles.py - 153 lines
  [LIB] sqla_compat.py - 495 lines
venv/lib/python3.10/site-packages/annotated_types/
  [LIB] __init__.py - 432 lines
venv/lib/python3.10/site-packages/anyio/
  [LIB] __init__.py - 85 lines
  [LIB] from_thread.py - 527 lines
  [LIB] lowlevel.py - 161 lines
  [TEST] pytest_plugin.py - 272 lines
  [LIB] to_interpreter.py - 218 lines
  [LIB] to_process.py - 258 lines
  [LIB] to_thread.py - 69 lines
venv/lib/python3.10/site-packages/anyio/_backends/
  [LIB] __init__.py - 0 lines
  [LIB] _asyncio.py - 2816 lines
  [LIB] _trio.py - 1334 lines
venv/lib/python3.10/site-packages/anyio/_core/
  [LIB] __init__.py - 0 lines
  [LIB] _asyncio_selector_thread.py - 167 lines
  [LIB] _eventloop.py - 166 lines
  [LIB] _exceptions.py - 126 lines
  [LIB] _fileio.py - 742 lines
  [LIB] _resources.py - 18 lines
  [LIB] _signals.py - 27 lines
  [LIB] _sockets.py - 792 lines
  [LIB] _streams.py - 52 lines
  [LIB] _subprocesses.py - 202 lines
  [LIB] _synchronization.py - 732 lines
  [LIB] _tasks.py - 158 lines
  [LIB] _tempfile.py - 616 lines
  [TEST] _testing.py - 78 lines
  [LIB] _typedattr.py - 81 lines
venv/lib/python3.10/site-packages/anyio/abc/
  [LIB] __init__.py - 55 lines
  [LIB] _eventloop.py - 376 lines
  [LIB] _resources.py - 33 lines
  [LIB] _sockets.py - 194 lines
  [LIB] _streams.py - 203 lines
  [LIB] _subprocesses.py - 79 lines
  [LIB] _tasks.py - 101 lines
  [TEST] _testing.py - 65 lines
venv/lib/python3.10/site-packages/anyio/streams/
  [LIB] __init__.py - 0 lines
  [LIB] buffered.py - 119 lines
  [LIB] file.py - 148 lines
  [LIB] memory.py - 317 lines
  [LIB] stapled.py - 141 lines
  [LIB] text.py - 147 lines
  [LIB] tls.py - 352 lines
venv/lib/python3.10/site-packages/async_timeout/
  [LIB] __init__.py - 276 lines
venv/lib/python3.10/site-packages/asyncpg/
  [LIB] __init__.py - 24 lines
  [LIB] _asyncio_compat.py - 94 lines
  [LIB] _version.py - 17 lines
  [LIB] cluster.py - 729 lines
  [LIB] compat.py - 88 lines
  [LIB] connect_utils.py - 1139 lines (ports: 5432)
  [LIB] connection.py - 2749 lines (ports: 4567)
  [LIB] connresource.py - 44 lines
  [LIB] cursor.py - 323 lines
  [LIB] introspection.py - 298 lines
  [LIB] pool.py - 1211 lines
  [LIB] prepared_stmt.py - 285 lines
  [SVC] serverversion.py - 70 lines
  [LIB] transaction.py - 246 lines
  [LIB] types.py - 223 lines
  [LIB] utils.py - 52 lines
venv/lib/python3.10/site-packages/asyncpg/_testbase/
  [LIB] __init__.py - 543 lines
  [LIB] fuzzer.py - 306 lines
venv/lib/python3.10/site-packages/asyncpg/exceptions/
  [LIB] __init__.py - 1211 lines
  [LIB] _base.py - 299 lines
venv/lib/python3.10/site-packages/asyncpg/pgproto/
  [LIB] __init__.py - 5 lines
  [LIB] types.py - 423 lines
venv/lib/python3.10/site-packages/asyncpg/protocol/
  [LIB] __init__.py - 11 lines
venv/lib/python3.10/site-packages/asyncpg/protocol/codecs/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/attr/
  [LIB] __init__.py - 104 lines
  [LIB] _cmp.py - 160 lines
  [LIB] _compat.py - 94 lines
  [CONFIG] _config.py - 31 lines
  [LIB] _funcs.py - 468 lines
  [LIB] _make.py - 3123 lines
  [LIB] _next_gen.py - 623 lines
  [LIB] _version_info.py - 86 lines
  [LIB] converters.py - 162 lines
  [LIB] exceptions.py - 95 lines
  [LIB] filters.py - 72 lines
  [LIB] setters.py - 79 lines
  [LIB] validators.py - 710 lines
venv/lib/python3.10/site-packages/attrs/
  [LIB] __init__.py - 69 lines
  [LIB] converters.py - 3 lines
  [LIB] exceptions.py - 3 lines
  [LIB] filters.py - 3 lines
  [LIB] setters.py - 3 lines
  [LIB] validators.py - 3 lines
venv/lib/python3.10/site-packages/click/
  [LIB] __init__.py - 123 lines
  [LIB] _compat.py - 622 lines
  [LIB] _termui_impl.py - 839 lines
  [LIB] _textwrap.py - 51 lines
  [LIB] _winconsole.py - 296 lines
  [LIB] core.py - 3135 lines
  [LIB] decorators.py - 551 lines
  [LIB] exceptions.py - 308 lines
  [LIB] formatting.py - 301 lines
  [LIB] globals.py - 67 lines
  [LIB] parser.py - 532 lines
  [LIB] shell_completion.py - 644 lines
  [LIB] termui.py - 877 lines
  [TEST] testing.py - 565 lines
  [LIB] types.py - 1165 lines
  [LIB] utils.py - 627 lines
venv/lib/python3.10/site-packages/dateutil/
  [LIB] __init__.py - 24 lines
  [LIB] _common.py - 43 lines
  [LIB] _version.py - 4 lines
  [LIB] easter.py - 89 lines
  [LIB] relativedelta.py - 599 lines
  [LIB] rrule.py - 1737 lines
  [LIB] tzwin.py - 2 lines
  [LIB] utils.py - 71 lines
venv/lib/python3.10/site-packages/dateutil/parser/
  [LIB] __init__.py - 61 lines
  [LIB] _parser.py - 1613 lines
  [LIB] isoparser.py - 416 lines
venv/lib/python3.10/site-packages/dateutil/tz/
  [LIB] __init__.py - 12 lines
  [LIB] _common.py - 419 lines
  [LIB] _factories.py - 80 lines
  [LIB] tz.py - 1849 lines
  [LIB] win.py - 370 lines
venv/lib/python3.10/site-packages/dateutil/zoneinfo/
  [LIB] __init__.py - 167 lines
  [LIB] rebuild.py - 75 lines
venv/lib/python3.10/site-packages/exceptiongroup/
  [LIB] __init__.py - 46 lines
  [LIB] _catch.py - 138 lines
  [LIB] _exceptions.py - 336 lines
  [LIB] _formatting.py - 601 lines
  [LIB] _suppress.py - 55 lines
  [LIB] _version.py - 21 lines
venv/lib/python3.10/site-packages/fastapi/
  [LIB] __init__.py - 25 lines
  [LIB] __main__.py - 3 lines
  [LIB] _compat.py - 664 lines
  [LIB] applications.py - 4588 lines
  [LIB] background.py - 59 lines
  [LIB] cli.py - 13 lines
  [LIB] concurrency.py - 39 lines
  [LIB] datastructures.py - 204 lines
  [LIB] encoders.py - 343 lines
  [LIB] exception_handlers.py - 34 lines
  [LIB] exceptions.py - 176 lines
  [LIB] logger.py - 3 lines
  [LIB] param_functions.py - 2360 lines
  [LIB] params.py - 786 lines
  [LIB] requests.py - 2 lines
  [LIB] responses.py - 48 lines
  [LIB] routing.py - 4440 lines
  [LIB] staticfiles.py - 1 lines
  [LIB] templating.py - 1 lines
  [TEST] testclient.py - 1 lines
  [LIB] types.py - 10 lines
  [LIB] utils.py - 220 lines
  [LIB] websockets.py - 3 lines
venv/lib/python3.10/site-packages/fastapi/dependencies/
  [LIB] __init__.py - 0 lines
  [LIB] models.py - 37 lines
  [LIB] utils.py - 1001 lines
venv/lib/python3.10/site-packages/fastapi/middleware/
  [LIB] __init__.py - 1 lines
  [LIB] cors.py - 1 lines
  [LIB] gzip.py - 1 lines
  [LIB] httpsredirect.py - 3 lines
  [LIB] trustedhost.py - 3 lines
  [LIB] wsgi.py - 1 lines
venv/lib/python3.10/site-packages/fastapi/openapi/
  [LIB] __init__.py - 0 lines
  [LIB] constants.py - 3 lines
  [LIB] docs.py - 344 lines
  [LIB] models.py - 445 lines
  [LIB] utils.py - 569 lines
venv/lib/python3.10/site-packages/fastapi/security/
  [LIB] __init__.py - 15 lines
  [LIB] api_key.py - 288 lines
  [LIB] base.py - 6 lines
  [LIB] http.py - 423 lines
  [LIB] oauth2.py - 653 lines
  [LIB] open_id_connect_url.py - 84 lines
  [LIB] utils.py - 10 lines
venv/lib/python3.10/site-packages/frozenlist/
  [LIB] __init__.py - 86 lines
venv/lib/python3.10/site-packages/greenlet/
  [LIB] __init__.py - 71 lines
venv/lib/python3.10/site-packages/greenlet/platform/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/greenlet/tests/
  [LIB] __init__.py - 240 lines
  [LIB] fail_clearing_run_switches.py - 47 lines
  [LIB] fail_cpp_exception.py - 33 lines
  [LIB] fail_initialstub_already_started.py - 78 lines
  [LIB] fail_slp_switch.py - 29 lines
  [LIB] fail_switch_three_greenlets.py - 44 lines
  [LIB] fail_switch_three_greenlets2.py - 55 lines
  [LIB] fail_switch_two_greenlets.py - 41 lines
  [LIB] leakcheck.py - 319 lines
venv/lib/python3.10/site-packages/h11/
  [LIB] __init__.py - 62 lines
  [LIB] _abnf.py - 132 lines
  [LIB] _connection.py - 659 lines
  [LIB] _events.py - 369 lines
  [LIB] _headers.py - 282 lines
  [LIB] _readers.py - 250 lines
  [LIB] _receivebuffer.py - 153 lines
  [LIB] _state.py - 365 lines
  [LIB] _util.py - 135 lines
  [LIB] _version.py - 16 lines
  [LIB] _writers.py - 145 lines
venv/lib/python3.10/site-packages/idna/
  [LIB] __init__.py - 45 lines
  [LIB] codec.py - 122 lines
  [LIB] compat.py - 15 lines
  [LIB] core.py - 437 lines
  [LIB] idnadata.py - 4243 lines
  [LIB] intranges.py - 57 lines
  [LIB] package_data.py - 1 lines
  [LIB] uts46data.py - 8681 lines
venv/lib/python3.10/site-packages/jinja2/
  [LIB] __init__.py - 38 lines
  [LIB] _identifier.py - 6 lines
  [LIB] async_utils.py - 99 lines
  [LIB] bccache.py - 408 lines
  [LIB] compiler.py - 1998 lines
  [LIB] constants.py - 20 lines
  [LIB] debug.py - 191 lines
  [LIB] defaults.py - 48 lines
  [LIB] environment.py - 1672 lines
  [LIB] exceptions.py - 166 lines
  [LIB] ext.py - 870 lines
  [LIB] filters.py - 1873 lines
  [LIB] idtracking.py - 318 lines
  [LIB] lexer.py - 868 lines
  [LIB] loaders.py - 693 lines
  [LIB] meta.py - 112 lines
  [LIB] nativetypes.py - 130 lines
  [LIB] nodes.py - 1206 lines
  [LIB] optimizer.py - 48 lines
  [LIB] parser.py - 1049 lines
  [LIB] runtime.py - 1062 lines
  [LIB] sandbox.py - 436 lines
  [TEST] tests.py - 256 lines
  [LIB] utils.py - 766 lines
  [LIB] visitor.py - 92 lines
venv/lib/python3.10/site-packages/joblib/
  [LIB] __init__.py - 163 lines
  [LIB] _cloudpickle_wrapper.py - 18 lines
  [LIB] _dask.py - 381 lines (ports: 8786)
  [LIB] _memmapping_reducer.py - 715 lines
  [LIB] _multiprocessing_helpers.py - 51 lines
  [LIB] _parallel_backends.py - 753 lines
  [LIB] _store_backends.py - 488 lines
  [LIB] _utils.py - 83 lines
  [LIB] backports.py - 195 lines
  [LIB] compressor.py - 572 lines
  [LIB] disk.py - 131 lines
  [LIB] executor.py - 131 lines
  [LIB] func_inspect.py - 379 lines
  [LIB] hashing.py - 270 lines
  [LIB] logger.py - 159 lines
  [LIB] memory.py - 1242 lines
  [LIB] numpy_pickle.py - 756 lines
  [LIB] numpy_pickle_compat.py - 250 lines
  [LIB] numpy_pickle_utils.py - 291 lines
  [LIB] parallel.py - 2075 lines
  [LIB] pool.py - 362 lines
  [TEST] testing.py - 96 lines
venv/lib/python3.10/site-packages/joblib/externals/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/joblib/externals/cloudpickle/
  [LIB] __init__.py - 18 lines
  [EXEC] cloudpickle.py - 1545 lines
  [LIB] cloudpickle_fast.py - 14 lines
venv/lib/python3.10/site-packages/joblib/externals/loky/
  [LIB] __init__.py - 45 lines
  [LIB] _base.py - 28 lines
  [LIB] cloudpickle_wrapper.py - 102 lines
  [LIB] initializers.py - 80 lines
  [LIB] process_executor.py - 1344 lines
  [LIB] reusable_executor.py - 294 lines
venv/lib/python3.10/site-packages/joblib/externals/loky/backend/
  [LIB] __init__.py - 14 lines
  [LIB] _posix_reduction.py - 67 lines
  [LIB] _win_reduction.py - 18 lines
  [LIB] context.py - 405 lines
  [LIB] fork_exec.py - 73 lines
  [LIB] popen_loky_posix.py - 193 lines
  [LIB] popen_loky_win32.py - 173 lines
  [LIB] process.py - 85 lines
  [LIB] queues.py - 236 lines
  [LIB] reduction.py - 223 lines
  [LIB] resource_tracker.py - 351 lines
  [EXEC] spawn.py - 244 lines
  [LIB] synchronize.py - 409 lines
  [LIB] utils.py - 181 lines
venv/lib/python3.10/site-packages/joblib/test/
  [LIB] __init__.py - 0 lines
  [LIB] common.py - 84 lines
  [TEST] testutils.py - 9 lines
venv/lib/python3.10/site-packages/joblib/test/data/
  [LIB] __init__.py - 0 lines
  [LIB] create_numpy_pickle.py - 106 lines
venv/lib/python3.10/site-packages/mako/
  [LIB] __init__.py - 8 lines
  [LIB] _ast_util.py - 713 lines
  [LIB] ast.py - 202 lines
  [LIB] cache.py - 239 lines
  [LIB] cmd.py - 99 lines
  [LIB] codegen.py - 1319 lines
  [LIB] compat.py - 70 lines
  [LIB] exceptions.py - 417 lines
  [LIB] filters.py - 163 lines
  [LIB] lexer.py - 481 lines
  [LIB] lookup.py - 361 lines
  [LIB] parsetree.py - 656 lines
  [LIB] pygen.py - 309 lines
  [LIB] pyparser.py - 235 lines
  [LIB] runtime.py - 968 lines
  [LIB] template.py - 711 lines
  [LIB] util.py - 388 lines
venv/lib/python3.10/site-packages/mako/ext/
  [LIB] __init__.py - 0 lines
  [LIB] autohandler.py - 70 lines
  [LIB] babelplugin.py - 57 lines
  [LIB] beaker_cache.py - 82 lines
  [LIB] extract.py - 129 lines
  [LIB] linguaplugin.py - 57 lines
  [LIB] preprocessors.py - 20 lines
  [LIB] pygmentplugin.py - 150 lines
  [LIB] turbogears.py - 61 lines
venv/lib/python3.10/site-packages/mako/testing/
  [LIB] __init__.py - 0 lines
  [CONFIG] _config.py - 128 lines
  [LIB] assertions.py - 166 lines
  [CONFIG] config.py - 17 lines
  [LIB] exclusions.py - 80 lines
  [LIB] fixtures.py - 119 lines
  [LIB] helpers.py - 71 lines
venv/lib/python3.10/site-packages/markupsafe/
  [LIB] __init__.py - 395 lines
  [LIB] _native.py - 8 lines
venv/lib/python3.10/site-packages/multidict/
  [LIB] __init__.py - 59 lines
  [LIB] _abc.py - 73 lines
  [LIB] _compat.py - 15 lines
  [LIB] _multidict_py.py - 1242 lines
venv/lib/python3.10/site-packages/numpy/
  [CONFIG] __config__.py - 170 lines
  [LIB] __init__.py - 547 lines
  [LIB] _array_api_info.py - 346 lines
  [CONFIG] _configtool.py - 39 lines
  [LIB] _distributor_init.py - 15 lines
  [LIB] _expired_attrs_2_0.py - 80 lines
  [LIB] _globals.py - 95 lines
  [TEST] _pytesttester.py - 200 lines
  [TEST] conftest.py - 261 lines
  [LIB] ctypeslib.py - 602 lines
  [LIB] dtypes.py - 41 lines
  [LIB] exceptions.py - 247 lines
  [LIB] matlib.py - 379 lines
  [LIB] version.py - 11 lines
venv/lib/python3.10/site-packages/numpy/_core/
  [LIB] __init__.py - 180 lines
  [LIB] _add_newdocs.py - 6974 lines
  [LIB] _add_newdocs_scalars.py - 389 lines
  [LIB] _asarray.py - 135 lines
  [LIB] _dtype.py - 374 lines
  [LIB] _dtype_ctypes.py - 120 lines
  [LIB] _exceptions.py - 172 lines
  [LIB] _internal.py - 963 lines
  [EXEC] _machar.py - 356 lines
  [LIB] _methods.py - 256 lines
  [LIB] _string_helpers.py - 100 lines
  [LIB] _type_aliases.py - 119 lines
  [CONFIG] _ufunc_config.py - 483 lines
  [LIB] arrayprint.py - 1756 lines
  [EXEC] cversions.py - 13 lines
  [LIB] defchararray.py - 1414 lines
  [LIB] einsumfunc.py - 1499 lines
  [LIB] fromnumeric.py - 4269 lines
  [LIB] function_base.py - 546 lines
  [LIB] getlimits.py - 747 lines
  [LIB] memmap.py - 361 lines
  [LIB] multiarray.py - 1754 lines
  [LIB] numeric.py - 2713 lines
  [LIB] numerictypes.py - 629 lines
  [LIB] overrides.py - 181 lines
  [LIB] printoptions.py - 32 lines
  [LIB] records.py - 1091 lines
  [LIB] shape_base.py - 1004 lines
  [LIB] strings.py - 1641 lines
  [LIB] umath.py - 40 lines
venv/lib/python3.10/site-packages/numpy/_core/tests/
  [LIB] _locales.py - 72 lines
  [LIB] _natype.py - 198 lines
venv/lib/python3.10/site-packages/numpy/_core/tests/examples/cython/
  [LIB] setup.py - 37 lines
venv/lib/python3.10/site-packages/numpy/_core/tests/examples/limited_api/
  [LIB] setup.py - 22 lines
venv/lib/python3.10/site-packages/numpy/_pyinstaller/
  [LIB] __init__.py - 0 lines
  [LIB] hook-numpy.py - 36 lines
venv/lib/python3.10/site-packages/numpy/_pyinstaller/tests/
  [LIB] __init__.py - 16 lines
  [LIB] pyinstaller-smoke.py - 32 lines
venv/lib/python3.10/site-packages/numpy/_typing/
  [LIB] __init__.py - 154 lines
  [LIB] _add_docstring.py - 153 lines
  [LIB] _array_like.py - 192 lines
  [LIB] _char_codes.py - 214 lines
  [LIB] _dtype_like.py - 249 lines
  [LIB] _extended_precision.py - 27 lines
  [LIB] _nbit.py - 19 lines
  [LIB] _nbit_base.py - 100 lines
  [LIB] _nested_sequence.py - 89 lines
  [LIB] _scalars.py - 27 lines
  [LIB] _shape.py - 7 lines
  [LIB] _ufunc.py - 7 lines
venv/lib/python3.10/site-packages/numpy/_utils/
  [LIB] __init__.py - 88 lines
  [LIB] _convertions.py - 18 lines
  [LIB] _inspect.py - 191 lines
  [LIB] _pep440.py - 487 lines
venv/lib/python3.10/site-packages/numpy/char/
  [LIB] __init__.py - 2 lines
venv/lib/python3.10/site-packages/numpy/compat/
  [LIB] __init__.py - 29 lines
  [LIB] py3k.py - 143 lines
venv/lib/python3.10/site-packages/numpy/compat/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/core/
  [LIB] __init__.py - 32 lines
  [LIB] _dtype.py - 9 lines
  [LIB] _dtype_ctypes.py - 9 lines
  [LIB] _internal.py - 25 lines
  [LIB] _multiarray_umath.py - 55 lines
  [LIB] _utils.py - 21 lines
  [LIB] arrayprint.py - 9 lines
  [LIB] defchararray.py - 9 lines
  [LIB] einsumfunc.py - 9 lines
  [LIB] fromnumeric.py - 9 lines
  [LIB] function_base.py - 9 lines
  [LIB] getlimits.py - 9 lines
  [LIB] multiarray.py - 24 lines
  [LIB] numeric.py - 11 lines
  [LIB] numerictypes.py - 9 lines
  [LIB] overrides.py - 9 lines
  [LIB] records.py - 9 lines
  [LIB] shape_base.py - 9 lines
  [LIB] umath.py - 9 lines
venv/lib/python3.10/site-packages/numpy/distutils/
  [LIB] __init__.py - 64 lines
  [LIB] _shell_utils.py - 87 lines
  [LIB] armccompiler.py - 26 lines
  [LIB] ccompiler.py - 826 lines
  [LIB] ccompiler_opt.py - 2668 lines
  [LIB] conv_template.py - 329 lines
  [LIB] core.py - 215 lines
  [LIB] cpuinfo.py - 683 lines
  [LIB] exec_command.py - 315 lines
  [LIB] extension.py - 101 lines
  [LIB] from_template.py - 261 lines
  [LIB] fujitsuccompiler.py - 28 lines
  [LIB] intelccompiler.py - 106 lines
  [EXEC] lib2def.py - 116 lines
  [LIB] line_endings.py - 77 lines
  [LIB] log.py - 111 lines
  [LIB] mingw32ccompiler.py - 597 lines
  [LIB] misc_util.py - 2484 lines
  [LIB] msvc9compiler.py - 63 lines
  [LIB] msvccompiler.py - 76 lines
  [CONFIG] npy_pkg_config.py - 441 lines
  [LIB] numpy_distribution.py - 17 lines
  [LIB] pathccompiler.py - 21 lines
  [LIB] system_info.py - 3267 lines
  [LIB] unixccompiler.py - 141 lines
venv/lib/python3.10/site-packages/numpy/distutils/command/
  [LIB] __init__.py - 41 lines
  [LIB] autodist.py - 148 lines
  [LIB] bdist_rpm.py - 22 lines
  [LIB] build.py - 62 lines
  [LIB] build_clib.py - 469 lines
  [LIB] build_ext.py - 752 lines
  [LIB] build_py.py - 31 lines
  [LIB] build_scripts.py - 49 lines
  [LIB] build_src.py - 773 lines
  [CONFIG] config.py - 516 lines
  [CONFIG] config_compiler.py - 126 lines
  [LIB] develop.py - 15 lines
  [LIB] egg_info.py - 25 lines
  [LIB] install.py - 79 lines
  [LIB] install_clib.py - 40 lines
  [LIB] install_data.py - 24 lines
  [LIB] install_headers.py - 25 lines
  [LIB] sdist.py - 27 lines
venv/lib/python3.10/site-packages/numpy/distutils/fcompiler/
  [EXEC] __init__.py - 1035 lines
  [EXEC] absoft.py - 156 lines
  [EXEC] arm.py - 71 lines
  [EXEC] compaq.py - 120 lines
  [LIB] environment.py - 88 lines
  [EXEC] fujitsu.py - 46 lines
  [EXEC] g95.py - 42 lines
  [EXEC] gnu.py - 555 lines
  [EXEC] hpux.py - 41 lines
  [EXEC] ibm.py - 97 lines
  [EXEC] intel.py - 211 lines
  [EXEC] lahey.py - 45 lines
  [EXEC] mips.py - 54 lines
  [EXEC] nag.py - 87 lines
  [EXEC] none.py - 28 lines
  [EXEC] nv.py - 53 lines
  [EXEC] pathf95.py - 33 lines
  [EXEC] pg.py - 128 lines
  [EXEC] sun.py - 51 lines
  [EXEC] vast.py - 52 lines
venv/lib/python3.10/site-packages/numpy/distutils/tests/
  [LIB] __init__.py - 0 lines
  [LIB] utilities.py - 90 lines
venv/lib/python3.10/site-packages/numpy/doc/
  [LIB] ufuncs.py - 138 lines
venv/lib/python3.10/site-packages/numpy/f2py/
  [LIB] __init__.py - 87 lines
  [LIB] __main__.py - 5 lines
  [LIB] __version__.py - 1 lines
  [LIB] _isocbind.py - 62 lines
  [LIB] _src_pyf.py - 240 lines
  [LIB] auxfuncs.py - 1000 lines
  [LIB] capi_maps.py - 821 lines
  [LIB] cb_rules.py - 644 lines
  [LIB] cfuncs.py - 1552 lines
  [LIB] common_rules.py - 146 lines
  [LIB] crackfortran.py - 3746 lines
  [LIB] diagnose.py - 154 lines
  [LIB] f2py2e.py - 783 lines
  [LIB] f90mod_rules.py - 270 lines
  [LIB] func2subr.py - 323 lines
  [LIB] rules.py - 1578 lines
  [LIB] symbolic.py - 1517 lines
  [LIB] use_rules.py - 106 lines
venv/lib/python3.10/site-packages/numpy/f2py/_backends/
  [LIB] __init__.py - 9 lines
  [LIB] _backend.py - 46 lines
  [LIB] _distutils.py - 75 lines
  [LIB] _meson.py - 233 lines
venv/lib/python3.10/site-packages/numpy/f2py/tests/
  [LIB] __init__.py - 15 lines
  [LIB] util.py - 441 lines
venv/lib/python3.10/site-packages/numpy/fft/
  [LIB] __init__.py - 215 lines
  [LIB] _helper.py - 235 lines
  [LIB] _pocketfft.py - 1687 lines
  [LIB] helper.py - 16 lines
venv/lib/python3.10/site-packages/numpy/fft/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/lib/
  [LIB] __init__.py - 94 lines
  [LIB] _array_utils_impl.py - 62 lines
  [LIB] _arraypad_impl.py - 891 lines
  [LIB] _arraysetops_impl.py - 1215 lines
  [LIB] _arrayterator_impl.py - 224 lines
  [LIB] _datasource.py - 700 lines
  [LIB] _function_base_impl.py - 5827 lines
  [LIB] _histograms_impl.py - 1090 lines
  [LIB] _index_tricks_impl.py - 1069 lines
  [LIB] _iotools.py - 899 lines
  [LIB] _nanfunctions_impl.py - 2028 lines
  [LIB] _npyio_impl.py - 2595 lines
  [LIB] _polynomial_impl.py - 1458 lines
  [LIB] _scimath_impl.py - 643 lines
  [LIB] _shape_base_impl.py - 1294 lines
  [LIB] _stride_tricks_impl.py - 549 lines
  [LIB] _twodim_base_impl.py - 1188 lines
  [LIB] _type_check_impl.py - 699 lines
  [LIB] _ufunclike_impl.py - 207 lines
  [EXEC] _user_array_impl.py - 291 lines
  [LIB] _utils_impl.py - 775 lines
  [LIB] _version.py - 155 lines
  [LIB] array_utils.py - 7 lines
  [LIB] format.py - 1008 lines
  [LIB] introspect.py - 95 lines
  [LIB] mixins.py - 182 lines
  [LIB] npyio.py - 3 lines
  [LIB] recfunctions.py - 1685 lines
  [LIB] scimath.py - 4 lines
  [LIB] stride_tricks.py - 3 lines
  [LIB] user_array.py - 1 lines
venv/lib/python3.10/site-packages/numpy/lib/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/linalg/
  [LIB] __init__.py - 95 lines
  [LIB] _linalg.py - 3629 lines
  [LIB] linalg.py - 16 lines
venv/lib/python3.10/site-packages/numpy/linalg/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/ma/
  [LIB] __init__.py - 54 lines
  [LIB] core.py - 8959 lines
  [LIB] extras.py - 2321 lines
  [LIB] mrecords.py - 774 lines
  [TEST] testutils.py - 292 lines
  [EXEC] timer_comparison.py - 442 lines
venv/lib/python3.10/site-packages/numpy/ma/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/matrixlib/
  [LIB] __init__.py - 11 lines
  [LIB] defmatrix.py - 1118 lines
venv/lib/python3.10/site-packages/numpy/matrixlib/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/polynomial/
  [LIB] __init__.py - 187 lines
  [LIB] _polybase.py - 1197 lines
  [LIB] chebyshev.py - 2003 lines
  [LIB] hermite.py - 1740 lines
  [LIB] hermite_e.py - 1642 lines
  [LIB] laguerre.py - 1675 lines
  [LIB] legendre.py - 1605 lines
  [LIB] polynomial.py - 1617 lines
  [LIB] polyutils.py - 757 lines
venv/lib/python3.10/site-packages/numpy/polynomial/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/random/
  [LIB] __init__.py - 215 lines
  [LIB] _pickle.py - 89 lines
venv/lib/python3.10/site-packages/numpy/random/_examples/cffi/
  [LIB] extending.py - 40 lines
  [LIB] parse.py - 54 lines
venv/lib/python3.10/site-packages/numpy/random/_examples/numba/
  [LIB] extending.py - 84 lines
  [LIB] extending_distributions.py - 67 lines
venv/lib/python3.10/site-packages/numpy/random/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/random/tests/data/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/rec/
  [LIB] __init__.py - 2 lines
venv/lib/python3.10/site-packages/numpy/strings/
  [LIB] __init__.py - 2 lines
venv/lib/python3.10/site-packages/numpy/testing/
  [LIB] __init__.py - 22 lines
  [LIB] overrides.py - 83 lines
  [EXEC] print_coercion_tables.py - 201 lines
venv/lib/python3.10/site-packages/numpy/testing/_private/
  [LIB] __init__.py - 0 lines
  [LIB] extbuild.py - 252 lines
  [LIB] utils.py - 2760 lines
venv/lib/python3.10/site-packages/numpy/testing/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/typing/
  [LIB] __init__.py - 175 lines
  [LIB] mypy_plugin.py - 199 lines
venv/lib/python3.10/site-packages/numpy/typing/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/numpy/typing/tests/data/pass/
  [LIB] arithmetic.py - 596 lines
  [LIB] array_constructors.py - 137 lines
  [LIB] array_like.py - 45 lines
  [LIB] arrayprint.py - 37 lines
  [LIB] arrayterator.py - 27 lines
  [LIB] bitwise_ops.py - 131 lines
  [LIB] comparisons.py - 315 lines
  [LIB] dtype.py - 57 lines
  [LIB] einsumfunc.py - 36 lines
  [LIB] flatiter.py - 16 lines
  [LIB] fromnumeric.py - 272 lines
  [LIB] index_tricks.py - 60 lines
  [LIB] lib_user_array.py - 22 lines
  [LIB] lib_utils.py - 19 lines
  [LIB] lib_version.py - 18 lines
  [LIB] literal.py - 51 lines
  [LIB] ma.py - 8 lines
  [LIB] mod.py - 149 lines
  [LIB] modules.py - 45 lines
  [LIB] multiarray.py - 76 lines
  [LIB] ndarray_conversion.py - 87 lines
  [LIB] ndarray_misc.py - 196 lines
  [LIB] ndarray_shape_manipulation.py - 47 lines
  [LIB] nditer.py - 4 lines
  [LIB] numeric.py - 95 lines
  [LIB] numerictypes.py - 17 lines
  [LIB] random.py - 1497 lines
  [LIB] recfunctions.py - 162 lines
  [LIB] scalars.py - 248 lines
  [LIB] shape.py - 21 lines
  [LIB] simple.py - 168 lines
  [LIB] simple_py3.py - 6 lines
  [CONFIG] ufunc_config.py - 64 lines
  [LIB] ufunclike.py - 47 lines
  [LIB] ufuncs.py - 16 lines
  [LIB] warnings_and_errors.py - 6 lines
venv/lib/python3.10/site-packages/pip/
  [LIB] __init__.py - 13 lines
  [LIB] __main__.py - 31 lines
venv/lib/python3.10/site-packages/pip/_internal/
  [LIB] __init__.py - 19 lines
  [LIB] build_env.py - 296 lines
  [LIB] cache.py - 264 lines
  [CONFIG] configuration.py - 366 lines
  [LIB] exceptions.py - 658 lines
  [LIB] main.py - 12 lines
  [LIB] pyproject.py - 168 lines
  [LIB] self_outdated_check.py - 189 lines
  [LIB] wheel_builder.py - 377 lines
venv/lib/python3.10/site-packages/pip/_internal/cli/
  [LIB] __init__.py - 4 lines
  [LIB] autocompletion.py - 171 lines
  [LIB] base_command.py - 220 lines
  [LIB] cmdoptions.py - 1018 lines
  [LIB] command_context.py - 27 lines
  [LIB] main.py - 70 lines
  [LIB] main_parser.py - 87 lines
  [LIB] parser.py - 292 lines
  [LIB] progress_bars.py - 321 lines
  [LIB] req_command.py - 506 lines
  [LIB] spinners.py - 157 lines
  [LIB] status_codes.py - 6 lines
venv/lib/python3.10/site-packages/pip/_internal/commands/
  [LIB] __init__.py - 127 lines
  [LIB] cache.py - 223 lines
  [LIB] check.py - 53 lines
  [LIB] completion.py - 96 lines
  [CONFIG] configuration.py - 266 lines
  [LIB] debug.py - 202 lines
  [LIB] download.py - 140 lines
  [LIB] freeze.py - 97 lines
  [LIB] hash.py - 59 lines
  [LIB] help.py - 41 lines
  [LIB] index.py - 139 lines
  [LIB] install.py - 771 lines
  [LIB] list.py - 363 lines
  [LIB] search.py - 174 lines
  [LIB] show.py - 178 lines
  [LIB] uninstall.py - 105 lines
  [LIB] wheel.py - 178 lines
venv/lib/python3.10/site-packages/pip/_internal/distributions/
  [LIB] __init__.py - 21 lines
  [LIB] base.py - 36 lines
  [LIB] installed.py - 20 lines
  [LIB] sdist.py - 127 lines
  [LIB] wheel.py - 31 lines
venv/lib/python3.10/site-packages/pip/_internal/index/
  [LIB] __init__.py - 2 lines
  [LIB] collector.py - 648 lines
  [LIB] package_finder.py - 1004 lines
  [LIB] sources.py - 224 lines
venv/lib/python3.10/site-packages/pip/_internal/locations/
  [LIB] __init__.py - 520 lines
  [LIB] _distutils.py - 169 lines
  [CONFIG] _sysconfig.py - 219 lines
  [LIB] base.py - 52 lines
venv/lib/python3.10/site-packages/pip/_internal/metadata/
  [LIB] __init__.py - 62 lines
  [LIB] base.py - 546 lines
  [LIB] pkg_resources.py - 256 lines
venv/lib/python3.10/site-packages/pip/_internal/models/
  [LIB] __init__.py - 2 lines
  [LIB] candidate.py - 34 lines
  [LIB] direct_url.py - 220 lines
  [LIB] format_control.py - 80 lines
  [LIB] index.py - 28 lines
  [LIB] link.py - 288 lines
  [LIB] scheme.py - 31 lines
  [LIB] search_scope.py - 129 lines
  [LIB] selection_prefs.py - 51 lines
  [LIB] target_python.py - 110 lines
  [LIB] wheel.py - 89 lines
venv/lib/python3.10/site-packages/pip/_internal/network/
  [LIB] __init__.py - 2 lines
  [LIB] auth.py - 323 lines
  [LIB] cache.py - 69 lines
  [LIB] download.py - 185 lines
  [LIB] lazy_wheel.py - 210 lines
  [LIB] session.py - 454 lines
  [LIB] utils.py - 96 lines
  [LIB] xmlrpc.py - 60 lines
venv/lib/python3.10/site-packages/pip/_internal/operations/
  [LIB] __init__.py - 0 lines
  [LIB] check.py - 149 lines
  [LIB] freeze.py - 254 lines
  [LIB] prepare.py - 642 lines
venv/lib/python3.10/site-packages/pip/_internal/operations/build/
  [LIB] __init__.py - 0 lines
  [LIB] metadata.py - 39 lines
  [LIB] metadata_editable.py - 41 lines
  [LIB] metadata_legacy.py - 74 lines
  [LIB] wheel.py - 37 lines
  [LIB] wheel_editable.py - 46 lines
  [LIB] wheel_legacy.py - 102 lines
venv/lib/python3.10/site-packages/pip/_internal/operations/install/
  [LIB] __init__.py - 2 lines
  [LIB] editable_legacy.py - 47 lines
  [LIB] legacy.py - 120 lines
  [LIB] wheel.py - 738 lines
venv/lib/python3.10/site-packages/pip/_internal/req/
  [LIB] __init__.py - 94 lines
  [LIB] constructors.py - 490 lines
  [LIB] req_file.py - 536 lines
  [LIB] req_install.py - 858 lines
  [LIB] req_set.py - 189 lines
  [LIB] req_tracker.py - 124 lines
  [LIB] req_uninstall.py - 633 lines
venv/lib/python3.10/site-packages/pip/_internal/resolution/
  [LIB] __init__.py - 0 lines
  [LIB] base.py - 20 lines
venv/lib/python3.10/site-packages/pip/_internal/resolution/legacy/
  [LIB] __init__.py - 0 lines
  [LIB] resolver.py - 467 lines
venv/lib/python3.10/site-packages/pip/_internal/resolution/resolvelib/
  [LIB] __init__.py - 0 lines
  [LIB] base.py - 141 lines
  [LIB] candidates.py - 547 lines
  [LIB] factory.py - 739 lines
  [LIB] found_candidates.py - 155 lines
  [LIB] provider.py - 248 lines
  [LIB] reporter.py - 68 lines
  [LIB] requirements.py - 166 lines
  [LIB] resolver.py - 292 lines
venv/lib/python3.10/site-packages/pip/_internal/utils/
  [LIB] __init__.py - 0 lines
  [LIB] _log.py - 38 lines
  [LIB] appdirs.py - 52 lines
  [LIB] compat.py - 63 lines
  [LIB] compatibility_tags.py - 165 lines
  [LIB] datetime.py - 11 lines
  [LIB] deprecation.py - 120 lines
  [LIB] direct_url_helpers.py - 87 lines
  [LIB] distutils_args.py - 42 lines
  [LIB] egg_link.py - 75 lines
  [LIB] encoding.py - 36 lines
  [LIB] entrypoints.py - 27 lines
  [LIB] filesystem.py - 182 lines
  [LIB] filetypes.py - 27 lines
  [LIB] glibc.py - 88 lines
  [LIB] hashes.py - 144 lines
  [LIB] inject_securetransport.py - 35 lines
  [LIB] logging.py - 343 lines
  [LIB] misc.py - 653 lines
  [LIB] models.py - 39 lines
  [LIB] packaging.py - 57 lines
  [LIB] setuptools_build.py - 195 lines
  [LIB] subprocess.py - 260 lines
  [LIB] temp_dir.py - 246 lines
  [LIB] unpacking.py - 258 lines
  [LIB] urls.py - 62 lines
  [LIB] virtualenv.py - 104 lines
  [LIB] wheel.py - 136 lines
venv/lib/python3.10/site-packages/pip/_internal/vcs/
  [LIB] __init__.py - 15 lines
  [LIB] bazaar.py - 101 lines
  [LIB] git.py - 526 lines
  [LIB] mercurial.py - 163 lines
  [LIB] subversion.py - 324 lines
  [LIB] versioncontrol.py - 705 lines
venv/lib/python3.10/site-packages/pip/_vendor/
  [LIB] __init__.py - 111 lines
  [LIB] distro.py - 1386 lines
  [LIB] six.py - 998 lines
  [LIB] typing_extensions.py - 2296 lines
venv/lib/python3.10/site-packages/pip/_vendor/cachecontrol/
  [LIB] __init__.py - 18 lines
  [LIB] _cmd.py - 61 lines
  [LIB] adapter.py - 137 lines
  [LIB] cache.py - 43 lines
  [LIB] compat.py - 32 lines
  [LIB] controller.py - 415 lines
  [LIB] filewrapper.py - 111 lines
  [LIB] heuristics.py - 139 lines
  [LIB] serialize.py - 186 lines
  [LIB] wrapper.py - 33 lines
venv/lib/python3.10/site-packages/pip/_vendor/cachecontrol/caches/
  [LIB] __init__.py - 6 lines
  [LIB] file_cache.py - 150 lines
  [LIB] redis_cache.py - 37 lines
venv/lib/python3.10/site-packages/pip/_vendor/certifi/
  [LIB] __init__.py - 3 lines
  [LIB] __main__.py - 12 lines
  [LIB] core.py - 76 lines
venv/lib/python3.10/site-packages/pip/_vendor/chardet/
  [LIB] __init__.py - 83 lines
  [LIB] big5freq.py - 386 lines
  [LIB] big5prober.py - 47 lines
  [LIB] chardistribution.py - 233 lines
  [LIB] charsetgroupprober.py - 107 lines
  [LIB] charsetprober.py - 145 lines
  [LIB] codingstatemachine.py - 88 lines
  [LIB] compat.py - 36 lines
  [LIB] cp949prober.py - 49 lines
  [LIB] enums.py - 76 lines
  [LIB] escprober.py - 101 lines
  [LIB] escsm.py - 246 lines
  [LIB] eucjpprober.py - 92 lines
  [LIB] euckrfreq.py - 195 lines
  [LIB] euckrprober.py - 47 lines
  [LIB] euctwfreq.py - 387 lines
  [LIB] euctwprober.py - 46 lines
  [LIB] gb2312freq.py - 283 lines
  [LIB] gb2312prober.py - 46 lines
  [LIB] hebrewprober.py - 292 lines
  [LIB] jisfreq.py - 325 lines
  [LIB] jpcntx.py - 233 lines
  [LIB] langbulgarianmodel.py - 4650 lines
  [LIB] langgreekmodel.py - 4398 lines
  [LIB] langhebrewmodel.py - 4383 lines
  [LIB] langhungarianmodel.py - 4650 lines
  [LIB] langrussianmodel.py - 5718 lines
  [LIB] langthaimodel.py - 4383 lines
  [LIB] langturkishmodel.py - 4383 lines
  [LIB] latin1prober.py - 145 lines
  [LIB] mbcharsetprober.py - 91 lines
  [LIB] mbcsgroupprober.py - 54 lines
  [LIB] mbcssm.py - 572 lines
  [LIB] sbcharsetprober.py - 145 lines
  [LIB] sbcsgroupprober.py - 83 lines
  [LIB] sjisprober.py - 92 lines
  [LIB] universaldetector.py - 286 lines
  [LIB] utf8prober.py - 82 lines
  [LIB] version.py - 9 lines
venv/lib/python3.10/site-packages/pip/_vendor/chardet/cli/
  [LIB] __init__.py - 1 lines
  [EXEC] chardetect.py - 84 lines
venv/lib/python3.10/site-packages/pip/_vendor/chardet/metadata/
  [LIB] __init__.py - 0 lines
  [LIB] languages.py - 310 lines (ports: 1993)
venv/lib/python3.10/site-packages/pip/_vendor/colorama/
  [LIB] __init__.py - 6 lines
  [LIB] ansi.py - 102 lines
  [LIB] ansitowin32.py - 258 lines
  [LIB] initialise.py - 80 lines
  [LIB] win32.py - 152 lines
  [LIB] winterm.py - 169 lines
venv/lib/python3.10/site-packages/pip/_vendor/distlib/
  [LIB] __init__.py - 23 lines
  [LIB] compat.py - 1116 lines
  [LIB] database.py - 1345 lines
  [LIB] index.py - 509 lines
  [LIB] locators.py - 1300 lines
  [LIB] manifest.py - 393 lines
  [LIB] markers.py - 152 lines
  [LIB] metadata.py - 1058 lines
  [LIB] resources.py - 358 lines
  [EXEC] scripts.py - 429 lines
  [LIB] util.py - 1932 lines
  [LIB] version.py - 739 lines
  [LIB] wheel.py - 1053 lines
venv/lib/python3.10/site-packages/pip/_vendor/html5lib/
  [LIB] __init__.py - 35 lines
  [LIB] _ihatexml.py - 289 lines
  [LIB] _inputstream.py - 918 lines
  [LIB] _tokenizer.py - 1735 lines
  [LIB] _utils.py - 159 lines
  [LIB] constants.py - 2946 lines
  [LIB] html5parser.py - 2795 lines
  [LIB] serializer.py - 409 lines
venv/lib/python3.10/site-packages/pip/_vendor/html5lib/_trie/
  [LIB] __init__.py - 5 lines
  [LIB] _base.py - 40 lines
  [LIB] py.py - 67 lines
venv/lib/python3.10/site-packages/pip/_vendor/html5lib/filters/
  [LIB] __init__.py - 0 lines
  [LIB] alphabeticalattributes.py - 29 lines
  [LIB] base.py - 12 lines
  [LIB] inject_meta_charset.py - 73 lines
  [LIB] lint.py - 93 lines
  [LIB] optionaltags.py - 207 lines
  [LIB] sanitizer.py - 916 lines
  [LIB] whitespace.py - 38 lines
venv/lib/python3.10/site-packages/pip/_vendor/html5lib/treeadapters/
  [LIB] __init__.py - 30 lines
  [LIB] genshi.py - 54 lines
  [LIB] sax.py - 50 lines
venv/lib/python3.10/site-packages/pip/_vendor/html5lib/treebuilders/
  [LIB] __init__.py - 88 lines
  [LIB] base.py - 417 lines
  [LIB] dom.py - 239 lines
  [LIB] etree.py - 343 lines
  [LIB] etree_lxml.py - 392 lines
venv/lib/python3.10/site-packages/pip/_vendor/html5lib/treewalkers/
  [LIB] __init__.py - 154 lines
  [LIB] base.py - 252 lines
  [LIB] dom.py - 43 lines
  [LIB] etree.py - 131 lines
  [LIB] etree_lxml.py - 215 lines
  [LIB] genshi.py - 69 lines
venv/lib/python3.10/site-packages/pip/_vendor/idna/
  [LIB] __init__.py - 44 lines
  [LIB] codec.py - 112 lines
  [LIB] compat.py - 13 lines
  [LIB] core.py - 397 lines
  [LIB] idnadata.py - 2137 lines
  [LIB] intranges.py - 54 lines
  [LIB] package_data.py - 2 lines
  [LIB] uts46data.py - 8512 lines
venv/lib/python3.10/site-packages/pip/_vendor/msgpack/
  [LIB] __init__.py - 54 lines
  [LIB] _version.py - 1 lines
  [LIB] exceptions.py - 48 lines
  [LIB] ext.py - 193 lines
  [LIB] fallback.py - 1012 lines
venv/lib/python3.10/site-packages/pip/_vendor/packaging/
  [LIB] __about__.py - 26 lines
  [LIB] __init__.py - 25 lines
  [LIB] _manylinux.py - 301 lines
  [LIB] _musllinux.py - 136 lines
  [LIB] _structures.py - 61 lines
  [LIB] markers.py - 304 lines
  [LIB] requirements.py - 146 lines
  [LIB] specifiers.py - 802 lines
  [LIB] tags.py - 487 lines
  [LIB] utils.py - 136 lines
  [LIB] version.py - 504 lines
venv/lib/python3.10/site-packages/pip/_vendor/pep517/
  [LIB] __init__.py - 6 lines
  [EXEC] build.py - 127 lines
  [EXEC] check.py - 207 lines
  [LIB] colorlog.py - 115 lines
  [LIB] compat.py - 51 lines
  [LIB] dirtools.py - 44 lines
  [LIB] envbuild.py - 171 lines
  [EXEC] meta.py - 92 lines
  [LIB] wrappers.py - 375 lines
venv/lib/python3.10/site-packages/pip/_vendor/pep517/in_process/
  [LIB] __init__.py - 17 lines
  [EXEC] _in_process.py - 363 lines
venv/lib/python3.10/site-packages/pip/_vendor/pkg_resources/
  [LIB] __init__.py - 3296 lines
  [LIB] py31compat.py - 23 lines
venv/lib/python3.10/site-packages/pip/_vendor/platformdirs/
  [LIB] __init__.py - 331 lines
  [LIB] __main__.py - 46 lines
  [LIB] android.py - 119 lines
  [LIB] api.py - 156 lines
  [LIB] macos.py - 64 lines
  [LIB] unix.py - 181 lines
  [LIB] version.py - 4 lines
  [LIB] windows.py - 182 lines
venv/lib/python3.10/site-packages/pip/_vendor/progress/
  [LIB] __init__.py - 189 lines
  [LIB] bar.py - 93 lines
  [LIB] colors.py - 79 lines
  [LIB] counter.py - 47 lines
  [LIB] spinner.py - 45 lines
venv/lib/python3.10/site-packages/pip/_vendor/pygments/
  [LIB] __init__.py - 83 lines
  [LIB] __main__.py - 17 lines
  [LIB] cmdline.py - 663 lines
  [LIB] console.py - 70 lines
  [LIB] filter.py - 71 lines
  [LIB] formatter.py - 94 lines
  [LIB] lexer.py - 879 lines (ports: 1024)
  [LIB] modeline.py - 43 lines
  [LIB] plugin.py - 69 lines
  [LIB] regexopt.py - 91 lines
  [LIB] scanner.py - 104 lines
  [LIB] sphinxext.py - 155 lines
  [LIB] style.py - 197 lines
  [LIB] token.py - 212 lines
  [EXEC] unistring.py - 153 lines
  [LIB] util.py - 308 lines
venv/lib/python3.10/site-packages/pip/_vendor/pygments/filters/
  [LIB] __init__.py - 937 lines
venv/lib/python3.10/site-packages/pip/_vendor/pygments/formatters/
  [LIB] __init__.py - 153 lines
  [EXEC] _mapping.py - 84 lines
  [LIB] bbcode.py - 108 lines
  [LIB] groff.py - 168 lines
  [LIB] html.py - 983 lines
  [LIB] img.py - 641 lines
  [LIB] irc.py - 179 lines
  [LIB] latex.py - 511 lines
  [LIB] other.py - 161 lines
  [LIB] pangomarkup.py - 83 lines
  [LIB] rtf.py - 146 lines
  [LIB] svg.py - 188 lines
  [LIB] terminal.py - 127 lines
  [LIB] terminal256.py - 338 lines
venv/lib/python3.10/site-packages/pip/_vendor/pygments/lexers/
  [LIB] __init__.py - 341 lines
  [EXEC] _mapping.py - 580 lines
  [LIB] python.py - 1188 lines
venv/lib/python3.10/site-packages/pip/_vendor/pygments/styles/
  [LIB] __init__.py - 93 lines
venv/lib/python3.10/site-packages/pip/_vendor/pyparsing/
  [LIB] __init__.py - 328 lines
  [LIB] actions.py - 207 lines
  [LIB] common.py - 424 lines
  [LIB] core.py - 5789 lines
  [LIB] exceptions.py - 267 lines
  [LIB] helpers.py - 1069 lines
  [LIB] results.py - 760 lines
  [TEST] testing.py - 331 lines
  [LIB] unicode.py - 332 lines
  [LIB] util.py - 235 lines
venv/lib/python3.10/site-packages/pip/_vendor/pyparsing/diagram/
  [LIB] __init__.py - 593 lines
venv/lib/python3.10/site-packages/pip/_vendor/requests/
  [LIB] __init__.py - 154 lines
  [LIB] __version__.py - 14 lines
  [LIB] _internal_utils.py - 42 lines
  [LIB] adapters.py - 538 lines
  [LIB] api.py - 159 lines
  [LIB] auth.py - 305 lines
  [EXEC] certs.py - 18 lines
  [LIB] compat.py - 77 lines
  [LIB] cookies.py - 549 lines
  [LIB] exceptions.py - 133 lines
  [EXEC] help.py - 132 lines
  [LIB] hooks.py - 34 lines
  [LIB] models.py - 973 lines
  [LIB] packages.py - 16 lines
  [LIB] sessions.py - 771 lines (ports: 3128,4012)
  [LIB] status_codes.py - 123 lines
  [LIB] structures.py - 105 lines
  [LIB] utils.py - 1060 lines
venv/lib/python3.10/site-packages/pip/_vendor/resolvelib/
  [LIB] __init__.py - 26 lines
  [LIB] providers.py - 133 lines
  [LIB] reporters.py - 43 lines
  [LIB] resolvers.py - 482 lines
  [LIB] structs.py - 165 lines
venv/lib/python3.10/site-packages/pip/_vendor/resolvelib/compat/
  [LIB] __init__.py - 0 lines
  [LIB] collections_abc.py - 6 lines
venv/lib/python3.10/site-packages/pip/_vendor/rich/
  [LIB] __init__.py - 172 lines
  [LIB] __main__.py - 280 lines
  [LIB] _cell_widths.py - 451 lines
  [LIB] _emoji_codes.py - 3610 lines
  [LIB] _emoji_replace.py - 32 lines
  [LIB] _extension.py - 10 lines
  [LIB] _inspect.py - 210 lines
  [LIB] _log_render.py - 94 lines
  [LIB] _loop.py - 43 lines
  [LIB] _lru_cache.py - 34 lines
  [LIB] _palettes.py - 309 lines
  [LIB] _pick.py - 17 lines
  [LIB] _ratio.py - 160 lines
  [LIB] _spinners.py - 848 lines
  [LIB] _stack.py - 16 lines
  [LIB] _timer.py - 19 lines
  [LIB] _windows.py - 72 lines
  [LIB] _wrap.py - 55 lines
  [LIB] abc.py - 33 lines
  [LIB] align.py - 312 lines
  [LIB] ansi.py - 228 lines
  [LIB] bar.py - 94 lines
  [LIB] box.py - 483 lines
  [LIB] cells.py - 147 lines
  [LIB] color.py - 581 lines
  [LIB] color_triplet.py - 38 lines
  [LIB] columns.py - 187 lines
  [LIB] console.py - 2211 lines
  [LIB] constrain.py - 37 lines
  [LIB] containers.py - 167 lines
  [LIB] control.py - 175 lines
  [LIB] default_styles.py - 183 lines
  [LIB] diagnose.py - 6 lines
  [LIB] emoji.py - 96 lines
  [LIB] errors.py - 34 lines
  [LIB] file_proxy.py - 54 lines
  [LIB] filesize.py - 89 lines
  [LIB] highlighter.py - 147 lines (ports: 7334)
  [LIB] json.py - 140 lines
  [LIB] jupyter.py - 92 lines
  [LIB] layout.py - 444 lines
  [LIB] live.py - 365 lines
  [LIB] live_render.py - 113 lines
  [LIB] logging.py - 268 lines (ports: 8080)
  [LIB] markup.py - 244 lines
  [LIB] measure.py - 149 lines
  [LIB] padding.py - 141 lines
  [LIB] pager.py - 34 lines
  [LIB] palette.py - 100 lines
  [LIB] panel.py - 250 lines
  [LIB] pretty.py - 903 lines
  [LIB] progress.py - 1036 lines
  [LIB] progress_bar.py - 216 lines
  [LIB] prompt.py - 376 lines
  [LIB] protocol.py - 42 lines
  [LIB] region.py - 10 lines
  [LIB] repr.py - 151 lines
  [LIB] rule.py - 115 lines
  [LIB] scope.py - 86 lines
  [LIB] screen.py - 54 lines
  [LIB] segment.py - 720 lines
  [LIB] spinner.py - 134 lines
  [LIB] status.py - 132 lines
  [LIB] style.py - 785 lines
  [LIB] styled.py - 42 lines
  [LIB] syntax.py - 735 lines
  [LIB] table.py - 968 lines
  [LIB] tabulate.py - 51 lines
  [LIB] terminal_theme.py - 55 lines
  [LIB] text.py - 1282 lines
  [LIB] theme.py - 112 lines
  [LIB] themes.py - 5 lines
  [LIB] traceback.py - 678 lines
  [LIB] tree.py - 249 lines
venv/lib/python3.10/site-packages/pip/_vendor/tenacity/
  [LIB] __init__.py - 517 lines
  [LIB] _asyncio.py - 92 lines
  [LIB] _utils.py - 68 lines
  [LIB] after.py - 46 lines
  [LIB] before.py - 41 lines
  [LIB] before_sleep.py - 58 lines
  [LIB] nap.py - 43 lines
  [LIB] retry.py - 213 lines
  [LIB] stop.py - 96 lines
  [LIB] tornadoweb.py - 59 lines
  [LIB] wait.py - 191 lines
venv/lib/python3.10/site-packages/pip/_vendor/tomli/
  [LIB] __init__.py - 6 lines
  [LIB] _parser.py - 703 lines
  [LIB] _re.py - 83 lines
venv/lib/python3.10/site-packages/pip/_vendor/urllib3/
  [LIB] __init__.py - 85 lines
  [LIB] _collections.py - 355 lines
  [LIB] _version.py - 2 lines
  [LIB] connection.py - 569 lines
  [LIB] connectionpool.py - 1113 lines
  [LIB] exceptions.py - 323 lines (ports: 8080)
  [LIB] fields.py - 274 lines
  [LIB] filepost.py - 98 lines
  [LIB] poolmanager.py - 555 lines (ports: 3128)
  [LIB] request.py - 170 lines
  [LIB] response.py - 821 lines
venv/lib/python3.10/site-packages/pip/_vendor/urllib3/contrib/
  [LIB] __init__.py - 0 lines
  [LIB] _appengine_environ.py - 36 lines
  [LIB] appengine.py - 314 lines
  [LIB] ntlmpool.py - 130 lines
  [LIB] pyopenssl.py - 511 lines
  [LIB] securetransport.py - 922 lines
  [LIB] socks.py - 216 lines
venv/lib/python3.10/site-packages/pip/_vendor/urllib3/contrib/_securetransport/
  [LIB] __init__.py - 0 lines
  [LIB] bindings.py - 519 lines
  [LIB] low_level.py - 397 lines
venv/lib/python3.10/site-packages/pip/_vendor/urllib3/packages/
  [LIB] __init__.py - 0 lines
  [LIB] six.py - 1077 lines
venv/lib/python3.10/site-packages/pip/_vendor/urllib3/packages/backports/
  [LIB] __init__.py - 0 lines
  [LIB] makefile.py - 51 lines
venv/lib/python3.10/site-packages/pip/_vendor/urllib3/util/
  [LIB] __init__.py - 49 lines
  [LIB] connection.py - 149 lines
  [LIB] proxy.py - 57 lines
  [LIB] queue.py - 22 lines
  [LIB] request.py - 143 lines
  [LIB] response.py - 107 lines
  [LIB] retry.py - 622 lines
  [LIB] ssl_.py - 495 lines
  [LIB] ssl_match_hostname.py - 161 lines
  [LIB] ssltransport.py - 221 lines
  [LIB] timeout.py - 268 lines
  [LIB] url.py - 432 lines
  [LIB] wait.py - 153 lines
venv/lib/python3.10/site-packages/pip/_vendor/webencodings/
  [LIB] __init__.py - 342 lines
  [LIB] labels.py - 231 lines (ports: 1987,1988,1989)
  [EXEC] mklabels.py - 59 lines
  [TEST] tests.py - 153 lines
  [LIB] x_user_defined.py - 325 lines
venv/lib/python3.10/site-packages/pkg_resources/
  [LIB] __init__.py - 3303 lines
venv/lib/python3.10/site-packages/pkg_resources/_vendor/
  [LIB] __init__.py - 0 lines
  [LIB] appdirs.py - 608 lines
  [LIB] pyparsing.py - 5742 lines
venv/lib/python3.10/site-packages/pkg_resources/_vendor/packaging/
  [LIB] __about__.py - 26 lines
  [LIB] __init__.py - 25 lines
  [LIB] _manylinux.py - 301 lines
  [LIB] _musllinux.py - 136 lines
  [LIB] _structures.py - 67 lines
  [LIB] markers.py - 304 lines
  [LIB] requirements.py - 146 lines
  [LIB] specifiers.py - 828 lines
  [LIB] tags.py - 484 lines
  [LIB] utils.py - 136 lines
  [LIB] version.py - 504 lines
venv/lib/python3.10/site-packages/pkg_resources/extern/
  [LIB] __init__.py - 73 lines
venv/lib/python3.10/site-packages/pkg_resources/tests/data/my-test-package-source/
  [LIB] setup.py - 6 lines
venv/lib/python3.10/site-packages/prometheus_client/
  [EXEC] __init__.py - 72 lines
  [LIB] asgi.py - 40 lines
  [LIB] context_managers.py - 82 lines
  [LIB] core.py - 34 lines
  [LIB] decorator.py - 427 lines
  [LIB] exposition.py - 679 lines
  [LIB] gc_collector.py - 45 lines
  [LIB] metrics.py - 753 lines
  [LIB] metrics_core.py - 415 lines
  [LIB] mmap_dict.py - 145 lines
  [LIB] multiprocess.py - 170 lines
  [LIB] parser.py - 367 lines
  [LIB] platform_collector.py - 59 lines
  [LIB] process_collector.py - 101 lines
  [LIB] registry.py - 168 lines
  [LIB] samples.py - 73 lines
  [LIB] utils.py - 24 lines
  [LIB] validation.py - 123 lines
  [LIB] values.py - 139 lines
venv/lib/python3.10/site-packages/prometheus_client/bridge/
  [LIB] __init__.py - 0 lines
  [LIB] graphite.py - 94 lines
venv/lib/python3.10/site-packages/prometheus_client/openmetrics/
  [LIB] __init__.py - 0 lines
  [LIB] exposition.py - 117 lines
  [LIB] parser.py - 653 lines
venv/lib/python3.10/site-packages/prometheus_client/twisted/
  [LIB] __init__.py - 3 lines
  [LIB] _exposition.py - 8 lines
venv/lib/python3.10/site-packages/propcache/
  [LIB] __init__.py - 32 lines
  [LIB] _helpers.py - 39 lines
  [LIB] _helpers_py.py - 60 lines
  [LIB] api.py - 8 lines
venv/lib/python3.10/site-packages/psutil/
  [LIB] __init__.py - 2407 lines
  [LIB] _common.py - 950 lines
  [LIB] _psaix.py - 565 lines
  [LIB] _psbsd.py - 971 lines
  [LIB] _pslinux.py - 2295 lines
  [LIB] _psosx.py - 544 lines
  [LIB] _psposix.py - 207 lines
  [LIB] _pssunos.py - 734 lines
  [LIB] _pswindows.py - 1103 lines
venv/lib/python3.10/site-packages/psutil/tests/
  [LIB] __init__.py - 2025 lines
  [LIB] __main__.py - 12 lines
venv/lib/python3.10/site-packages/pydantic/
  [LIB] __init__.py - 445 lines
  [LIB] _migration.py - 308 lines
  [LIB] alias_generators.py - 62 lines
  [LIB] aliases.py - 135 lines
  [LIB] annotated_handlers.py - 122 lines
  [LIB] class_validators.py - 5 lines
  [LIB] color.py - 604 lines
  [CONFIG] config.py - 1213 lines
  [LIB] dataclasses.py - 383 lines
  [LIB] datetime_parse.py - 5 lines
  [LIB] decorator.py - 5 lines
  [LIB] env_settings.py - 5 lines
  [LIB] error_wrappers.py - 5 lines
  [LIB] errors.py - 189 lines
  [LIB] fields.py - 1559 lines
  [LIB] functional_serializers.py - 450 lines
  [LIB] functional_validators.py - 828 lines
  [LIB] generics.py - 5 lines
  [LIB] json.py - 5 lines
  [LIB] json_schema.py - 2695 lines
  [LIB] main.py - 1773 lines
  [LIB] mypy.py - 1380 lines
  [LIB] networks.py - 1312 lines (ports: 3306,4222,5432,6379,8000,9000,9092,27017)
  [LIB] parse.py - 5 lines
  [LIB] root_model.py - 157 lines
  [LIB] schema.py - 5 lines
  [LIB] tools.py - 5 lines
  [LIB] type_adapter.py - 727 lines
  [LIB] types.py - 3285 lines
  [LIB] typing.py - 5 lines
  [LIB] utils.py - 5 lines
  [LIB] validate_call_decorator.py - 116 lines
  [LIB] validators.py - 5 lines
  [LIB] version.py - 84 lines
  [LIB] warnings.py - 96 lines
venv/lib/python3.10/site-packages/pydantic/_internal/
  [LIB] __init__.py - 0 lines
  [CONFIG] _config.py - 373 lines
  [LIB] _core_metadata.py - 97 lines
  [LIB] _core_utils.py - 182 lines
  [LIB] _dataclasses.py - 238 lines
  [LIB] _decorators.py - 838 lines
  [LIB] _decorators_v1.py - 174 lines
  [LIB] _discriminated_union.py - 479 lines
  [LIB] _docs_extraction.py - 108 lines
  [LIB] _fields.py - 515 lines
  [LIB] _forward_ref.py - 23 lines
  [LIB] _generate_schema.py - 2904 lines
  [LIB] _generics.py - 547 lines
  [LIB] _git.py - 27 lines
  [LIB] _import_utils.py - 20 lines
  [LIB] _internal_dataclass.py - 7 lines
  [LIB] _known_annotated_metadata.py - 393 lines
  [LIB] _mock_val_ser.py - 228 lines
  [LIB] _model_construction.py - 792 lines
  [LIB] _namespace_utils.py - 293 lines
  [LIB] _repr.py - 125 lines
  [LIB] _schema_gather.py - 209 lines
  [LIB] _schema_generation_shared.py - 125 lines
  [LIB] _serializers.py - 53 lines
  [LIB] _signature.py - 188 lines
  [LIB] _typing_extra.py - 714 lines
  [LIB] _utils.py - 431 lines
  [LIB] _validate_call.py - 140 lines
  [LIB] _validators.py - 532 lines
venv/lib/python3.10/site-packages/pydantic/deprecated/
  [LIB] __init__.py - 0 lines
  [LIB] class_validators.py - 256 lines
  [CONFIG] config.py - 72 lines
  [LIB] copy_internals.py - 224 lines
  [LIB] decorator.py - 284 lines
  [LIB] json.py - 141 lines
  [LIB] parse.py - 80 lines
  [LIB] tools.py - 103 lines
venv/lib/python3.10/site-packages/pydantic/experimental/
  [LIB] __init__.py - 10 lines
  [LIB] arguments_schema.py - 44 lines
  [LIB] pipeline.py - 667 lines
venv/lib/python3.10/site-packages/pydantic/plugin/
  [LIB] __init__.py - 188 lines
  [LIB] _loader.py - 57 lines
  [LIB] _schema_validator.py - 140 lines
venv/lib/python3.10/site-packages/pydantic/v1/
  [LIB] __init__.py - 131 lines
  [LIB] _hypothesis_plugin.py - 391 lines
  [LIB] annotated_types.py - 72 lines
  [LIB] class_validators.py - 361 lines
  [LIB] color.py - 494 lines
  [CONFIG] config.py - 191 lines
  [LIB] dataclasses.py - 500 lines
  [LIB] datetime_parse.py - 248 lines
  [LIB] decorator.py - 264 lines
  [LIB] env_settings.py - 350 lines
  [LIB] error_wrappers.py - 161 lines
  [LIB] errors.py - 646 lines
  [LIB] fields.py - 1253 lines
  [LIB] generics.py - 400 lines
  [LIB] json.py - 112 lines
  [LIB] main.py - 1113 lines
  [LIB] mypy.py - 949 lines
  [LIB] networks.py - 747 lines
  [LIB] parse.py - 66 lines
  [LIB] schema.py - 1163 lines
  [LIB] tools.py - 92 lines
  [LIB] types.py - 1205 lines
  [LIB] typing.py - 615 lines
  [LIB] utils.py - 806 lines
  [LIB] validators.py - 768 lines
  [LIB] version.py - 38 lines
venv/lib/python3.10/site-packages/pydantic_core/
  [LIB] __init__.py - 144 lines
  [LIB] core_schema.py - 4325 lines
venv/lib/python3.10/site-packages/pytz/
  [EXEC] __init__.py - 1556 lines
  [LIB] exceptions.py - 59 lines
  [LIB] lazy.py - 172 lines
  [LIB] reference.py - 140 lines
  [EXEC] tzfile.py - 133 lines
  [LIB] tzinfo.py - 580 lines
venv/lib/python3.10/site-packages/redis/
  [LIB] __init__.py - 87 lines
  [LIB] backoff.py - 183 lines
  [LIB] cache.py - 401 lines
  [LIB] client.py - 1635 lines (ports: 6379)
  [LIB] cluster.py - 3352 lines (ports: 6379)
  [LIB] connection.py - 1822 lines (ports: 6379)
  [LIB] crc.py - 23 lines
  [LIB] credentials.py - 65 lines
  [LIB] event.py - 394 lines
  [LIB] exceptions.py - 241 lines
  [LIB] lock.py - 343 lines
  [LIB] ocsp.py - 308 lines
  [LIB] retry.py - 95 lines
  [LIB] sentinel.py - 410 lines
  [LIB] typing.py - 57 lines
  [LIB] utils.py - 310 lines
venv/lib/python3.10/site-packages/redis/_parsers/
  [LIB] __init__.py - 27 lines
  [LIB] base.py - 289 lines
  [LIB] commands.py - 281 lines
  [LIB] encoders.py - 44 lines
  [LIB] helpers.py - 882 lines
  [LIB] hiredis.py - 295 lines
  [LIB] resp2.py - 132 lines
  [LIB] resp3.py - 257 lines
  [LIB] socket.py - 162 lines
venv/lib/python3.10/site-packages/redis/asyncio/
  [LIB] __init__.py - 64 lines
  [LIB] client.py - 1618 lines (ports: 6379)
  [LIB] cluster.py - 2398 lines (ports: 6379)
  [LIB] connection.py - 1331 lines (ports: 6379)
  [LIB] lock.py - 334 lines
  [LIB] retry.py - 79 lines
  [LIB] sentinel.py - 389 lines
  [LIB] utils.py - 28 lines
venv/lib/python3.10/site-packages/redis/auth/
  [LIB] __init__.py - 0 lines
  [LIB] err.py - 31 lines
  [LIB] idp.py - 28 lines
  [LIB] token.py - 130 lines
  [LIB] token_manager.py - 370 lines
venv/lib/python3.10/site-packages/redis/commands/
  [LIB] __init__.py - 18 lines
  [LIB] cluster.py - 919 lines
  [LIB] core.py - 6672 lines
  [LIB] helpers.py - 118 lines
  [LIB] redismodules.py - 101 lines
  [LIB] sentinel.py - 99 lines
venv/lib/python3.10/site-packages/redis/commands/bf/
  [LIB] __init__.py - 253 lines
  [LIB] commands.py - 538 lines
  [LIB] info.py - 120 lines
venv/lib/python3.10/site-packages/redis/commands/json/
  [LIB] __init__.py - 147 lines
  [LIB] _util.py - 3 lines
  [LIB] commands.py - 431 lines
  [LIB] decoders.py - 60 lines
  [LIB] path.py - 16 lines
venv/lib/python3.10/site-packages/redis/commands/search/
  [LIB] __init__.py - 189 lines
  [LIB] _util.py - 7 lines
  [LIB] aggregation.py - 401 lines
  [LIB] commands.py - 1156 lines
  [LIB] dialect.py - 3 lines
  [LIB] document.py - 17 lines
  [LIB] field.py - 210 lines
  [LIB] index_definition.py - 79 lines
  [LIB] profile_information.py - 14 lines
  [LIB] query.py - 381 lines
  [LIB] querystring.py - 317 lines
  [LIB] reducers.py - 182 lines
  [LIB] result.py - 87 lines
  [LIB] suggestion.py - 55 lines
venv/lib/python3.10/site-packages/redis/commands/timeseries/
  [LIB] __init__.py - 108 lines
  [LIB] commands.py - 1136 lines
  [LIB] info.py - 91 lines
  [LIB] utils.py - 44 lines
venv/lib/python3.10/site-packages/redis/commands/vectorset/
  [LIB] __init__.py - 46 lines
  [LIB] commands.py - 367 lines
  [LIB] utils.py - 94 lines
venv/lib/python3.10/site-packages/scipy/
  [CONFIG] __config__.py - 161 lines
  [LIB] __init__.py - 141 lines
  [LIB] _distributor_init.py - 18 lines
  [TEST] conftest.py - 552 lines
  [LIB] version.py - 12 lines
venv/lib/python3.10/site-packages/scipy/_lib/
  [LIB] __init__.py - 14 lines
  [LIB] _array_api.py - 606 lines
  [LIB] _array_api_no_0d.py - 103 lines
  [LIB] _bunch.py - 225 lines
  [LIB] _ccallback.py - 251 lines
  [LIB] _disjoint_set.py - 254 lines
  [LIB] _docscrape.py - 761 lines
  [LIB] _elementwise_iterative_method.py - 357 lines
  [LIB] _finite_differences.py - 145 lines
  [LIB] _gcutils.py - 105 lines
  [LIB] _pep440.py - 487 lines
  [TEST] _testutils.py - 369 lines
  [LIB] _threadsafety.py - 58 lines
  [LIB] _tmpdirs.py - 86 lines
  [LIB] _util.py - 1179 lines
  [LIB] decorator.py - 399 lines
  [LIB] deprecation.py - 274 lines
  [LIB] doccer.py - 372 lines
  [LIB] uarray.py - 31 lines
venv/lib/python3.10/site-packages/scipy/_lib/_uarray/
  [LIB] __init__.py - 116 lines
  [LIB] _backend.py - 707 lines
venv/lib/python3.10/site-packages/scipy/_lib/array_api_compat/
  [LIB] __init__.py - 22 lines
  [LIB] _internal.py - 46 lines
venv/lib/python3.10/site-packages/scipy/_lib/array_api_compat/common/
  [LIB] __init__.py - 1 lines
  [LIB] _aliases.py - 555 lines
  [LIB] _fft.py - 183 lines
  [LIB] _helpers.py - 825 lines
  [LIB] _linalg.py - 156 lines
  [LIB] _typing.py - 23 lines
venv/lib/python3.10/site-packages/scipy/_lib/array_api_compat/cupy/
  [LIB] __init__.py - 16 lines
  [LIB] _aliases.py - 136 lines
  [LIB] _info.py - 326 lines
  [LIB] _typing.py - 46 lines
  [LIB] fft.py - 36 lines
  [LIB] linalg.py - 49 lines
venv/lib/python3.10/site-packages/scipy/_lib/array_api_compat/dask/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/_lib/array_api_compat/dask/array/
  [LIB] __init__.py - 9 lines
  [LIB] _aliases.py - 217 lines
  [LIB] _info.py - 345 lines
  [LIB] fft.py - 24 lines
  [LIB] linalg.py - 73 lines
venv/lib/python3.10/site-packages/scipy/_lib/array_api_compat/numpy/
  [LIB] __init__.py - 30 lines
  [LIB] _aliases.py - 141 lines
  [LIB] _info.py - 346 lines
  [LIB] _typing.py - 46 lines
  [LIB] fft.py - 29 lines
  [LIB] linalg.py - 90 lines
venv/lib/python3.10/site-packages/scipy/_lib/array_api_compat/torch/
  [LIB] __init__.py - 24 lines
  [LIB] _aliases.py - 752 lines
  [LIB] _info.py - 358 lines
  [LIB] fft.py - 86 lines
  [LIB] linalg.py - 121 lines
venv/lib/python3.10/site-packages/scipy/_lib/array_api_extra/
  [LIB] __init__.py - 15 lines
  [LIB] _funcs.py - 484 lines
  [LIB] _typing.py - 8 lines
venv/lib/python3.10/site-packages/scipy/_lib/cobyqa/
  [LIB] __init__.py - 20 lines
  [LIB] framework.py - 1240 lines
  [LIB] main.py - 1506 lines
  [LIB] models.py - 1529 lines
  [LIB] problem.py - 1296 lines
  [LIB] settings.py - 132 lines
venv/lib/python3.10/site-packages/scipy/_lib/cobyqa/subsolvers/
  [LIB] __init__.py - 14 lines
  [LIB] geometry.py - 387 lines
  [LIB] optim.py - 1203 lines
venv/lib/python3.10/site-packages/scipy/_lib/cobyqa/utils/
  [LIB] __init__.py - 18 lines
  [LIB] exceptions.py - 22 lines
  [LIB] math.py - 77 lines
  [LIB] versions.py - 67 lines
venv/lib/python3.10/site-packages/scipy/_lib/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/cluster/
  [LIB] __init__.py - 31 lines
  [LIB] hierarchy.py - 4178 lines
  [LIB] vq.py - 828 lines
venv/lib/python3.10/site-packages/scipy/cluster/tests/
  [LIB] __init__.py - 0 lines
  [TEST] hierarchy_test_data.py - 145 lines
venv/lib/python3.10/site-packages/scipy/constants/
  [LIB] __init__.py - 358 lines
  [LIB] _codata.py - 2266 lines
  [LIB] _constants.py - 366 lines
  [LIB] codata.py - 21 lines
  [LIB] constants.py - 53 lines
venv/lib/python3.10/site-packages/scipy/constants/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/datasets/
  [LIB] __init__.py - 90 lines
  [LIB] _download_all.py - 57 lines
  [LIB] _fetchers.py - 219 lines
  [LIB] _registry.py - 26 lines
  [LIB] _utils.py - 81 lines
venv/lib/python3.10/site-packages/scipy/datasets/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/differentiate/
  [LIB] __init__.py - 27 lines
  [LIB] _differentiate.py - 1129 lines
venv/lib/python3.10/site-packages/scipy/differentiate/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/fft/
  [LIB] __init__.py - 114 lines
  [LIB] _backend.py - 196 lines
  [LIB] _basic.py - 1630 lines
  [LIB] _basic_backend.py - 197 lines
  [LIB] _debug_backends.py - 22 lines
  [LIB] _fftlog.py - 223 lines
  [LIB] _fftlog_backend.py - 200 lines
  [LIB] _helper.py - 379 lines
  [LIB] _realtransforms.py - 693 lines
  [LIB] _realtransforms_backend.py - 63 lines
venv/lib/python3.10/site-packages/scipy/fft/_pocketfft/
  [LIB] __init__.py - 9 lines
  [LIB] basic.py - 251 lines
  [LIB] helper.py - 221 lines
  [LIB] realtransforms.py - 109 lines
venv/lib/python3.10/site-packages/scipy/fft/_pocketfft/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/fft/tests/
  [LIB] __init__.py - 0 lines
  [LIB] mock_backend.py - 96 lines
venv/lib/python3.10/site-packages/scipy/fftpack/
  [LIB] __init__.py - 103 lines
  [LIB] _basic.py - 428 lines
  [LIB] _helper.py - 115 lines
  [LIB] _pseudo_diffs.py - 554 lines
  [LIB] _realtransforms.py - 598 lines
  [LIB] basic.py - 20 lines
  [LIB] helper.py - 19 lines
  [LIB] pseudo_diffs.py - 22 lines
  [LIB] realtransforms.py - 19 lines
venv/lib/python3.10/site-packages/scipy/fftpack/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/integrate/
  [LIB] __init__.py - 122 lines
  [LIB] _bvp.py - 1154 lines
  [LIB] _cubature.py - 728 lines
  [LIB] _lebedev.py - 5450 lines
  [LIB] _ode.py - 1388 lines
  [LIB] _odepack_py.py - 273 lines
  [LIB] _quad_vec.py - 682 lines
  [LIB] _quadpack_py.py - 1279 lines
  [LIB] _quadrature.py - 1336 lines
  [LIB] _tanhsinh.py - 1384 lines (ports: 2007)
  [LIB] dop.py - 15 lines
  [LIB] lsoda.py - 15 lines
  [LIB] odepack.py - 17 lines
  [LIB] quadpack.py - 23 lines
  [LIB] vode.py - 15 lines
venv/lib/python3.10/site-packages/scipy/integrate/_ivp/
  [LIB] __init__.py - 8 lines
  [LIB] base.py - 290 lines
  [LIB] bdf.py - 478 lines
  [LIB] common.py - 451 lines
  [LIB] dop853_coefficients.py - 193 lines
  [LIB] ivp.py - 755 lines
  [LIB] lsoda.py - 224 lines
  [LIB] radau.py - 572 lines
  [LIB] rk.py - 601 lines
venv/lib/python3.10/site-packages/scipy/integrate/_ivp/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/integrate/_rules/
  [LIB] __init__.py - 12 lines
  [LIB] _base.py - 518 lines
  [LIB] _gauss_kronrod.py - 202 lines
  [LIB] _gauss_legendre.py - 62 lines
  [LIB] _genz_malik.py - 210 lines
venv/lib/python3.10/site-packages/scipy/integrate/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/interpolate/
  [LIB] __init__.py - 216 lines
  [LIB] _bary_rational.py - 715 lines
  [LIB] _bsplines.py - 2416 lines
  [LIB] _cubic.py - 958 lines
  [LIB] _fitpack2.py - 2394 lines
  [LIB] _fitpack_impl.py - 805 lines
  [LIB] _fitpack_py.py - 898 lines
  [LIB] _fitpack_repro.py - 992 lines
  [LIB] _interpolate.py - 2248 lines
  [LIB] _ndbspline.py - 420 lines
  [LIB] _ndgriddata.py - 332 lines
  [LIB] _pade.py - 67 lines
  [LIB] _polyint.py - 961 lines
  [LIB] _rbf.py - 290 lines
  [LIB] _rbfinterp.py - 550 lines
  [LIB] _rgi.py - 759 lines
  [LIB] dfitpack.py - 44 lines
  [LIB] fitpack.py - 31 lines
  [LIB] fitpack2.py - 29 lines
  [LIB] interpnd.py - 25 lines
  [LIB] interpolate.py - 30 lines
  [LIB] ndgriddata.py - 23 lines
  [LIB] polyint.py - 24 lines
  [LIB] rbf.py - 18 lines
venv/lib/python3.10/site-packages/scipy/interpolate/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/io/
  [LIB] __init__.py - 116 lines
  [LIB] _fortran.py - 354 lines
  [LIB] _idl.py - 919 lines
  [LIB] _mmio.py - 968 lines
  [LIB] _netcdf.py - 1094 lines
  [LIB] harwell_boeing.py - 17 lines
  [LIB] idl.py - 17 lines
  [LIB] mmio.py - 17 lines
  [LIB] netcdf.py - 17 lines
  [LIB] wavfile.py - 891 lines
venv/lib/python3.10/site-packages/scipy/io/_fast_matrix_market/
  [LIB] __init__.py - 598 lines
venv/lib/python3.10/site-packages/scipy/io/_harwell_boeing/
  [LIB] __init__.py - 7 lines
  [LIB] _fortran_format_parser.py - 313 lines
  [LIB] hb.py - 575 lines
venv/lib/python3.10/site-packages/scipy/io/_harwell_boeing/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/io/arff/
  [LIB] __init__.py - 28 lines
  [LIB] _arffread.py - 873 lines
  [LIB] arffread.py - 19 lines
venv/lib/python3.10/site-packages/scipy/io/arff/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/io/matlab/
  [LIB] __init__.py - 64 lines
  [LIB] _byteordercodes.py - 75 lines
  [LIB] _mio.py - 372 lines
  [LIB] _mio4.py - 632 lines
  [LIB] _mio5.py - 895 lines
  [LIB] _mio5_params.py - 281 lines
  [LIB] _miobase.py - 432 lines
  [LIB] byteordercodes.py - 17 lines
  [LIB] mio.py - 16 lines
  [LIB] mio4.py - 17 lines
  [LIB] mio5.py - 19 lines
  [LIB] mio5_params.py - 18 lines
  [LIB] mio5_utils.py - 17 lines
  [LIB] mio_utils.py - 17 lines
  [LIB] miobase.py - 16 lines
  [LIB] streams.py - 16 lines
venv/lib/python3.10/site-packages/scipy/io/matlab/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/io/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/linalg/
  [LIB] __init__.py - 236 lines
  [LIB] _basic.py - 2119 lines
  [LIB] _decomp.py - 1632 lines
  [LIB] _decomp_cholesky.py - 398 lines
  [LIB] _decomp_cossin.py - 221 lines
  [LIB] _decomp_ldl.py - 353 lines
  [LIB] _decomp_lu.py - 389 lines
  [LIB] _decomp_polar.py - 111 lines
  [LIB] _decomp_qr.py - 490 lines
  [LIB] _decomp_qz.py - 449 lines
  [LIB] _decomp_schur.py - 334 lines
  [LIB] _decomp_svd.py - 534 lines (ports: 2008)
  [LIB] _expm_frechet.py - 413 lines
  [LIB] _matfuncs.py - 867 lines (ports: 1185)
  [LIB] _matfuncs_inv_ssq.py - 886 lines
  [LIB] _matfuncs_sqrtm.py - 205 lines
  [LIB] _misc.py - 191 lines
  [LIB] _procrustes.py - 111 lines
  [LIB] _sketches.py - 178 lines
  [LIB] _solvers.py - 857 lines
  [LIB] _special_matrices.py - 1332 lines
  [TEST] _testutils.py - 65 lines
  [LIB] basic.py - 23 lines
  [LIB] blas.py - 484 lines
  [LIB] decomp.py - 23 lines
  [LIB] decomp_cholesky.py - 21 lines
  [LIB] decomp_lu.py - 21 lines
  [LIB] decomp_qr.py - 20 lines
  [LIB] decomp_schur.py - 21 lines
  [LIB] decomp_svd.py - 21 lines
  [LIB] interpolative.py - 989 lines
  [LIB] lapack.py - 1061 lines
  [LIB] matfuncs.py - 23 lines
  [LIB] misc.py - 21 lines
  [LIB] special_matrices.py - 22 lines
venv/lib/python3.10/site-packages/scipy/linalg/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/misc/
  [LIB] __init__.py - 6 lines
  [LIB] common.py - 6 lines
  [LIB] doccer.py - 6 lines
venv/lib/python3.10/site-packages/scipy/ndimage/
  [LIB] __init__.py - 173 lines
  [LIB] _delegators.py - 297 lines
  [LIB] _filters.py - 1965 lines
  [LIB] _fourier.py - 306 lines
  [LIB] _interpolation.py - 1003 lines
  [LIB] _measurements.py - 1687 lines
  [LIB] _morphology.py - 2629 lines
  [LIB] _ndimage_api.py - 16 lines
  [LIB] _ni_docstrings.py - 210 lines
  [LIB] _ni_support.py - 143 lines
  [LIB] _support_alternative_backends.py - 72 lines
  [LIB] filters.py - 27 lines
  [LIB] fourier.py - 21 lines
  [LIB] interpolation.py - 22 lines
  [LIB] measurements.py - 24 lines
  [LIB] morphology.py - 27 lines
venv/lib/python3.10/site-packages/scipy/ndimage/tests/
  [LIB] __init__.py - 12 lines
venv/lib/python3.10/site-packages/scipy/odr/
  [LIB] __init__.py - 131 lines
  [LIB] _add_newdocs.py - 34 lines
  [LIB] _models.py - 315 lines
  [LIB] _odrpack.py - 1154 lines
  [LIB] models.py - 20 lines
  [LIB] odrpack.py - 21 lines
venv/lib/python3.10/site-packages/scipy/odr/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/optimize/
  [LIB] __init__.py - 460 lines
  [LIB] _basinhopping.py - 735 lines
  [LIB] _bracket.py - 713 lines
  [LIB] _chandrupatla.py - 552 lines
  [LIB] _cobyla_py.py - 316 lines
  [LIB] _cobyqa_py.py - 72 lines
  [LIB] _constraints.py - 594 lines
  [LIB] _dcsrch.py - 728 lines
  [LIB] _differentiable_functions.py - 694 lines
  [LIB] _differentialevolution.py - 1969 lines
  [LIB] _direct_py.py - 280 lines
  [LIB] _dual_annealing.py - 732 lines
  [LIB] _elementwise.py - 801 lines
  [LIB] _hessian_update_strategy.py - 479 lines
  [LIB] _isotonic.py - 157 lines
  [LIB] _lbfgsb_py.py - 578 lines
  [LIB] _linesearch.py - 896 lines
  [LIB] _linprog.py - 733 lines
  [LIB] _linprog_doc.py - 1434 lines
  [LIB] _linprog_highs.py - 422 lines
  [LIB] _linprog_ip.py - 1126 lines
  [LIB] _linprog_rs.py - 572 lines
  [LIB] _linprog_simplex.py - 663 lines
  [LIB] _linprog_util.py - 1523 lines
  [LIB] _milp.py - 392 lines
  [LIB] _minimize.py - 1131 lines
  [LIB] _minpack_py.py - 1171 lines
  [LIB] _nnls.py - 97 lines
  [LIB] _nonlin.py - 1603 lines
  [LIB] _numdiff.py - 785 lines
  [LIB] _optimize.py - 4131 lines
  [LIB] _qap.py - 760 lines
  [LIB] _remove_redundancy.py - 522 lines
  [LIB] _root.py - 732 lines
  [LIB] _root_scalar.py - 538 lines
  [LIB] _shgo.py - 1600 lines
  [LIB] _slsqp_py.py - 511 lines
  [LIB] _spectral.py - 260 lines
  [LIB] _tnc.py - 431 lines
  [LIB] _trustregion.py - 304 lines
  [LIB] _trustregion_dogleg.py - 122 lines
  [LIB] _trustregion_exact.py - 438 lines
  [LIB] _trustregion_krylov.py - 65 lines
  [LIB] _trustregion_ncg.py - 126 lines
  [LIB] _tstutils.py - 972 lines
  [LIB] _zeros_py.py - 1395 lines
  [LIB] cobyla.py - 19 lines
  [LIB] elementwise.py - 38 lines
  [LIB] lbfgsb.py - 23 lines
  [LIB] linesearch.py - 18 lines
  [LIB] minpack.py - 27 lines
  [LIB] minpack2.py - 17 lines
  [LIB] moduleTNC.py - 19 lines
  [LIB] nonlin.py - 29 lines
  [LIB] optimize.py - 40 lines
  [LIB] slsqp.py - 23 lines
  [LIB] tnc.py - 22 lines
  [LIB] zeros.py - 26 lines
venv/lib/python3.10/site-packages/scipy/optimize/_highspy/
  [LIB] __init__.py - 0 lines
  [LIB] _highs_wrapper.py - 338 lines
venv/lib/python3.10/site-packages/scipy/optimize/_lsq/
  [LIB] __init__.py - 5 lines
  [LIB] bvls.py - 183 lines
  [LIB] common.py - 731 lines
  [LIB] dogbox.py - 331 lines
  [LIB] least_squares.py - 972 lines
  [LIB] lsq_linear.py - 361 lines
  [LIB] trf.py - 560 lines
  [LIB] trf_linear.py - 249 lines
venv/lib/python3.10/site-packages/scipy/optimize/_shgo_lib/
  [LIB] __init__.py - 0 lines
  [LIB] _complex.py - 1225 lines
  [LIB] _vertex.py - 460 lines
venv/lib/python3.10/site-packages/scipy/optimize/_trlib/
  [LIB] __init__.py - 12 lines
venv/lib/python3.10/site-packages/scipy/optimize/_trustregion_constr/
  [LIB] __init__.py - 6 lines
  [LIB] canonical_constraint.py - 390 lines
  [LIB] equality_constrained_sqp.py - 231 lines
  [LIB] minimize_trustregion_constr.py - 576 lines
  [LIB] projections.py - 407 lines
  [LIB] qp_subproblem.py - 637 lines
  [LIB] report.py - 49 lines
  [LIB] tr_interior_point.py - 361 lines
venv/lib/python3.10/site-packages/scipy/optimize/_trustregion_constr/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/optimize/cython_optimize/
  [LIB] __init__.py - 133 lines
venv/lib/python3.10/site-packages/scipy/optimize/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/signal/
  [LIB] __init__.py - 327 lines
  [LIB] _arraytools.py - 264 lines
  [LIB] _czt.py - 575 lines
  [LIB] _filter_design.py - 5663 lines
  [LIB] _fir_filter_design.py - 1286 lines
  [LIB] _lti_conversion.py - 533 lines
  [LIB] _ltisys.py - 3519 lines
  [LIB] _max_len_seq.py - 139 lines
  [LIB] _peak_finding.py - 1310 lines (ports: 4000)
  [LIB] _savitzky_golay.py - 357 lines
  [LIB] _short_time_fft.py - 1738 lines
  [LIB] _signaltools.py - 4989 lines
  [LIB] _spectral_py.py - 2291 lines
  [LIB] _spline_filters.py - 808 lines
  [LIB] _upfirdn.py - 216 lines
  [LIB] _waveforms.py - 696 lines
  [LIB] _wavelets.py - 29 lines
  [LIB] bsplines.py - 21 lines
  [LIB] filter_design.py - 28 lines
  [LIB] fir_filter_design.py - 20 lines
  [LIB] lti_conversion.py - 20 lines
  [LIB] ltisys.py - 25 lines
  [LIB] signaltools.py - 27 lines
  [LIB] spectral.py - 21 lines
  [LIB] spline.py - 25 lines
  [LIB] waveforms.py - 20 lines
  [LIB] wavelets.py - 17 lines
venv/lib/python3.10/site-packages/scipy/signal/tests/
  [LIB] __init__.py - 0 lines
  [TEST] _scipy_spectral_test_shim.py - 480 lines
  [LIB] mpsig.py - 122 lines
venv/lib/python3.10/site-packages/scipy/signal/windows/
  [LIB] __init__.py - 52 lines
  [LIB] _windows.py - 2374 lines
  [LIB] windows.py - 23 lines
venv/lib/python3.10/site-packages/scipy/sparse/
  [LIB] __init__.py - 331 lines
  [LIB] _base.py - 1448 lines
  [LIB] _bsr.py - 877 lines
  [LIB] _compressed.py - 1500 lines
  [LIB] _construct.py - 1402 lines
  [LIB] _coo.py - 1647 lines
  [LIB] _csc.py - 367 lines
  [LIB] _csr.py - 558 lines
  [LIB] _data.py - 569 lines
  [LIB] _dia.py - 590 lines
  [LIB] _dok.py - 692 lines
  [LIB] _extract.py - 178 lines
  [LIB] _index.py - 444 lines
  [LIB] _lil.py - 632 lines
  [LIB] _matrix.py - 146 lines
  [LIB] _matrix_io.py - 167 lines
  [LIB] _spfuncs.py - 76 lines
  [LIB] _sputils.py - 617 lines
  [LIB] base.py - 33 lines
  [LIB] bsr.py - 36 lines
  [LIB] compressed.py - 43 lines
  [LIB] construct.py - 44 lines
  [LIB] coo.py - 37 lines
  [LIB] csc.py - 25 lines
  [LIB] csr.py - 27 lines
  [LIB] data.py - 23 lines
  [LIB] dia.py - 29 lines
  [LIB] dok.py - 32 lines
  [LIB] extract.py - 23 lines
  [LIB] lil.py - 22 lines
  [LIB] sparsetools.py - 17 lines
  [LIB] spfuncs.py - 17 lines
  [LIB] sputils.py - 17 lines
venv/lib/python3.10/site-packages/scipy/sparse/csgraph/
  [LIB] __init__.py - 210 lines
  [LIB] _laplacian.py - 563 lines
  [LIB] _validation.py - 66 lines
venv/lib/python3.10/site-packages/scipy/sparse/csgraph/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/
  [LIB] __init__.py - 148 lines
  [LIB] _expm_multiply.py - 816 lines
  [LIB] _interface.py - 921 lines
  [LIB] _matfuncs.py - 940 lines
  [LIB] _norm.py - 195 lines
  [LIB] _onenormest.py - 467 lines
  [LIB] _special_sparse_arrays.py - 948 lines
  [LIB] _svdp.py - 309 lines
  [LIB] dsolve.py - 22 lines
  [LIB] eigen.py - 21 lines
  [LIB] interface.py - 20 lines
  [LIB] isolve.py - 22 lines
  [LIB] matfuncs.py - 18 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/_dsolve/
  [LIB] __init__.py - 71 lines
  [LIB] _add_newdocs.py - 147 lines
  [LIB] linsolve.py - 873 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/_dsolve/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/_eigen/
  [LIB] __init__.py - 22 lines
  [LIB] _svds.py - 540 lines
  [LIB] _svds_doc.py - 382 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/_eigen/arpack/
  [LIB] __init__.py - 20 lines
  [LIB] arpack.py - 1700 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/_eigen/arpack/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/_eigen/lobpcg/
  [LIB] __init__.py - 16 lines
  [LIB] lobpcg.py - 1110 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/_eigen/lobpcg/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/_eigen/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/_isolve/
  [LIB] __init__.py - 20 lines
  [LIB] _gcrotmk.py - 503 lines
  [LIB] iterative.py - 1045 lines
  [LIB] lgmres.py - 230 lines
  [LIB] lsmr.py - 486 lines
  [LIB] lsqr.py - 589 lines
  [LIB] minres.py - 372 lines
  [LIB] tfqmr.py - 179 lines
  [LIB] utils.py - 127 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/_isolve/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/sparse/linalg/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/sparse/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/spatial/
  [LIB] __init__.py - 129 lines
  [LIB] _geometric_slerp.py - 238 lines
  [LIB] _kdtree.py - 920 lines
  [LIB] _plotutils.py - 274 lines
  [LIB] _procrustes.py - 132 lines
  [LIB] _spherical_voronoi.py - 341 lines
  [LIB] ckdtree.py - 18 lines
  [LIB] distance.py - 3140 lines
  [LIB] kdtree.py - 25 lines
  [LIB] qhull.py - 25 lines
venv/lib/python3.10/site-packages/scipy/spatial/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/spatial/transform/
  [LIB] __init__.py - 29 lines
  [LIB] _rotation_groups.py - 140 lines
  [LIB] _rotation_spline.py - 460 lines
  [LIB] rotation.py - 21 lines
venv/lib/python3.10/site-packages/scipy/spatial/transform/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/special/
  [LIB] __init__.py - 887 lines
  [LIB] _add_newdocs.py - 10699 lines
  [LIB] _basic.py - 3579 lines
  [LIB] _ellip_harm.py - 214 lines
  [LIB] _input_validation.py - 17 lines
  [LIB] _lambertw.py - 149 lines
  [LIB] _logsumexp.py - 417 lines
  [TEST] _mptestutils.py - 453 lines
  [LIB] _multiufuncs.py - 610 lines
  [LIB] _orthogonal.py - 2592 lines
  [LIB] _sf_error.py - 15 lines
  [LIB] _spfun_stats.py - 106 lines
  [LIB] _spherical_bessel.py - 397 lines
  [LIB] _support_alternative_backends.py - 202 lines
  [TEST] _testutils.py - 321 lines
  [LIB] add_newdocs.py - 15 lines
  [LIB] basic.py - 87 lines
  [LIB] orthogonal.py - 45 lines
  [LIB] sf_error.py - 20 lines
  [LIB] specfun.py - 24 lines
  [LIB] spfun_stats.py - 17 lines
venv/lib/python3.10/site-packages/scipy/special/_precompute/
  [LIB] __init__.py - 0 lines
  [LIB] cosine_cdf.py - 17 lines
  [LIB] expn_asy.py - 54 lines
  [LIB] gammainc_asy.py - 116 lines
  [LIB] gammainc_data.py - 124 lines
  [LIB] hyp2f1_data.py - 484 lines
  [EXEC] lambertw.py - 68 lines
  [EXEC] loggamma.py - 43 lines
  [LIB] struve_convergence.py - 131 lines
  [LIB] utils.py - 38 lines
  [EXEC] wright_bessel.py - 342 lines
  [LIB] wright_bessel_data.py - 152 lines
  [EXEC] wrightomega.py - 41 lines
  [EXEC] zetac.py - 27 lines
venv/lib/python3.10/site-packages/scipy/special/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/special/tests/data/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/stats/
  [LIB] __init__.py - 667 lines
  [LIB] _axis_nan_policy.py - 699 lines
  [LIB] _binned_statistic.py - 795 lines
  [TEST] _binomtest.py - 375 lines
  [TEST] _bws_test.py - 177 lines
  [LIB] _censored_data.py - 459 lines
  [LIB] _common.py - 5 lines
  [LIB] _constants.py - 42 lines
  [LIB] _continuous_distns.py - 12516 lines (ports: 7974)
  [LIB] _correlation.py - 210 lines
  [LIB] _covariance.py - 633 lines
  [LIB] _crosstab.py - 204 lines
  [LIB] _discrete_distns.py - 2091 lines
  [LIB] _distn_infrastructure.py - 4174 lines
  [LIB] _distr_params.py - 299 lines
  [LIB] _distribution_infrastructure.py - 5068 lines
  [LIB] _entropy.py - 429 lines
  [LIB] _fit.py - 1351 lines
  [TEST] _hypotests.py - 2027 lines
  [LIB] _kde.py - 728 lines
  [LIB] _ksstats.py - 600 lines
  [LIB] _mannwhitneyu.py - 492 lines
  [LIB] _mgc.py - 550 lines
  [LIB] _morestats.py - 4581 lines
  [LIB] _mstats_basic.py - 3662 lines
  [LIB] _mstats_extras.py - 521 lines
  [LIB] _multicomp.py - 449 lines
  [LIB] _multivariate.py - 7305 lines
  [LIB] _new_distributions.py - 375 lines
  [LIB] _odds_ratio.py - 466 lines
  [TEST] _page_trend_test.py - 479 lines
  [LIB] _probability_distribution.py - 1742 lines
  [LIB] _qmc.py - 2951 lines (ports: 2635)
  [LIB] _qmvnt.py - 533 lines
  [LIB] _relative_risk.py - 263 lines
  [LIB] _resampling.py - 2377 lines
  [LIB] _result_classes.py - 40 lines
  [LIB] _sampling.py - 1314 lines
  [LIB] _sensitivity_analysis.py - 713 lines
  [LIB] _stats_mstats_common.py - 303 lines
  [LIB] _stats_py.py - 11015 lines
  [LIB] _survival.py - 683 lines (ports: 1073)
  [LIB] _tukeylambda_stats.py - 199 lines
  [LIB] _variation.py - 128 lines
  [LIB] _warnings_errors.py - 38 lines
  [LIB] _wilcoxon.py - 259 lines
  [LIB] biasedurn.py - 16 lines
  [LIB] contingency.py - 521 lines
  [LIB] distributions.py - 24 lines
  [LIB] kde.py - 18 lines
  [LIB] morestats.py - 27 lines
  [LIB] mstats.py - 140 lines
  [LIB] mstats_basic.py - 42 lines
  [LIB] mstats_extras.py - 25 lines
  [LIB] mvn.py - 17 lines
  [LIB] qmc.py - 236 lines
  [LIB] sampling.py - 73 lines
  [LIB] stats.py - 41 lines
venv/lib/python3.10/site-packages/scipy/stats/_levy_stable/
  [LIB] __init__.py - 1239 lines
venv/lib/python3.10/site-packages/scipy/stats/_rcont/
  [LIB] __init__.py - 4 lines
venv/lib/python3.10/site-packages/scipy/stats/_unuran/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/scipy/stats/tests/
  [LIB] __init__.py - 0 lines
  [TEST] common_tests.py - 354 lines
venv/lib/python3.10/site-packages/scipy/stats/tests/data/
  [LIB] _mvt.py - 171 lines
  [LIB] fisher_exact_results_from_r.py - 607 lines
venv/lib/python3.10/site-packages/setuptools/
  [LIB] __init__.py - 242 lines
  [LIB] _deprecation_warning.py - 7 lines
  [LIB] _imp.py - 82 lines
  [LIB] archive_util.py - 205 lines
  [LIB] build_meta.py - 290 lines
  [CONFIG] config.py - 751 lines
  [LIB] dep_util.py - 25 lines
  [LIB] depends.py - 176 lines
  [LIB] dist.py - 1156 lines
  [LIB] errors.py - 40 lines
  [LIB] extension.py - 55 lines
  [LIB] glob.py - 167 lines
  [LIB] installer.py - 104 lines
  [EXEC] launch.py - 36 lines
  [LIB] monkey.py - 177 lines
  [LIB] msvc.py - 1805 lines
  [LIB] namespaces.py - 107 lines
  [LIB] package_index.py - 1176 lines
  [LIB] py34compat.py - 13 lines
  [LIB] sandbox.py - 530 lines
  [LIB] unicode_utils.py - 42 lines
  [LIB] version.py - 6 lines
  [LIB] wheel.py - 213 lines
  [LIB] windows_support.py - 29 lines
venv/lib/python3.10/site-packages/setuptools/_distutils/
  [LIB] __init__.py - 24 lines
  [LIB] _msvccompiler.py - 561 lines
  [LIB] archive_util.py - 256 lines
  [LIB] bcppcompiler.py - 393 lines
  [LIB] ccompiler.py - 1123 lines
  [LIB] cmd.py - 403 lines
  [CONFIG] config.py - 130 lines
  [LIB] core.py - 249 lines
  [LIB] cygwinccompiler.py - 425 lines
  [LIB] debug.py - 5 lines
  [LIB] dep_util.py - 92 lines
  [LIB] dir_util.py - 210 lines
  [LIB] dist.py - 1257 lines
  [LIB] errors.py - 97 lines
  [LIB] extension.py - 240 lines
  [LIB] fancy_getopt.py - 457 lines
  [LIB] file_util.py - 238 lines
  [LIB] filelist.py - 355 lines
  [LIB] log.py - 77 lines
  [LIB] msvc9compiler.py - 788 lines
  [LIB] msvccompiler.py - 643 lines
  [LIB] py35compat.py - 19 lines
  [LIB] py38compat.py - 7 lines
  [LIB] spawn.py - 106 lines
  [CONFIG] sysconfig.py - 601 lines
  [LIB] text_file.py - 286 lines
  [LIB] unixccompiler.py - 325 lines
  [LIB] util.py - 548 lines
  [LIB] version.py - 363 lines
  [LIB] versionpredicate.py - 169 lines
venv/lib/python3.10/site-packages/setuptools/_distutils/command/
  [LIB] __init__.py - 31 lines
  [LIB] bdist.py - 143 lines
  [LIB] bdist_dumb.py - 123 lines
  [LIB] bdist_msi.py - 749 lines
  [LIB] bdist_rpm.py - 579 lines
  [LIB] bdist_wininst.py - 377 lines
  [LIB] build.py - 157 lines
  [LIB] build_clib.py - 209 lines
  [LIB] build_ext.py - 755 lines
  [LIB] build_py.py - 392 lines
  [LIB] build_scripts.py - 152 lines
  [LIB] check.py - 148 lines
  [LIB] clean.py - 76 lines
  [CONFIG] config.py - 344 lines
  [LIB] install.py - 721 lines
  [LIB] install_data.py - 79 lines
  [LIB] install_egg_info.py - 84 lines
  [LIB] install_headers.py - 47 lines
  [LIB] install_lib.py - 217 lines
  [LIB] install_scripts.py - 60 lines
  [LIB] py37compat.py - 30 lines
  [LIB] register.py - 304 lines
  [LIB] sdist.py - 494 lines
  [LIB] upload.py - 214 lines
venv/lib/python3.10/site-packages/setuptools/_vendor/
  [LIB] __init__.py - 0 lines
  [LIB] ordered_set.py - 488 lines
  [LIB] pyparsing.py - 5742 lines
venv/lib/python3.10/site-packages/setuptools/_vendor/more_itertools/
  [LIB] __init__.py - 4 lines
  [LIB] more.py - 3825 lines
  [LIB] recipes.py - 620 lines
venv/lib/python3.10/site-packages/setuptools/_vendor/packaging/
  [LIB] __about__.py - 26 lines
  [LIB] __init__.py - 25 lines
  [LIB] _manylinux.py - 301 lines
  [LIB] _musllinux.py - 136 lines
  [LIB] _structures.py - 67 lines
  [LIB] markers.py - 304 lines
  [LIB] requirements.py - 146 lines
  [LIB] specifiers.py - 828 lines
  [LIB] tags.py - 484 lines
  [LIB] utils.py - 136 lines
  [LIB] version.py - 504 lines
venv/lib/python3.10/site-packages/setuptools/command/
  [LIB] __init__.py - 8 lines
  [LIB] alias.py - 78 lines
  [LIB] bdist_egg.py - 456 lines
  [LIB] bdist_rpm.py - 40 lines
  [LIB] build_clib.py - 101 lines
  [LIB] build_ext.py - 328 lines
  [LIB] build_py.py - 242 lines
  [LIB] develop.py - 193 lines
  [LIB] dist_info.py - 36 lines
  [EXEC] easy_install.py - 2354 lines
  [LIB] egg_info.py - 755 lines
  [LIB] install.py - 132 lines
  [LIB] install_egg_info.py - 82 lines
  [LIB] install_lib.py - 148 lines
  [LIB] install_scripts.py - 69 lines
  [LIB] py36compat.py - 134 lines
  [LIB] register.py - 18 lines
  [LIB] rotate.py - 64 lines
  [LIB] saveopts.py - 22 lines
  [LIB] sdist.py - 196 lines
  [LIB] setopt.py - 149 lines
  [TEST] test.py - 252 lines
  [LIB] upload.py - 17 lines
  [LIB] upload_docs.py - 202 lines
venv/lib/python3.10/site-packages/setuptools/extern/
  [LIB] __init__.py - 73 lines
venv/lib/python3.10/site-packages/sklearn/
  [LIB] __init__.py - 162 lines
  [LIB] _built_with_meson.py - 0 lines
  [CONFIG] _config.py - 407 lines
  [LIB] _distributor_init.py - 13 lines
  [LIB] _min_dependencies.py - 74 lines
  [LIB] base.py - 1369 lines
  [LIB] calibration.py - 1448 lines
  [TEST] conftest.py - 375 lines
  [LIB] discriminant_analysis.py - 1129 lines
  [LIB] dummy.py - 704 lines
  [LIB] exceptions.py - 249 lines
  [LIB] isotonic.py - 517 lines
  [LIB] kernel_approximation.py - 1106 lines
  [LIB] kernel_ridge.py - 240 lines
  [LIB] multiclass.py - 1287 lines
  [LIB] multioutput.py - 1328 lines
  [LIB] naive_bayes.py - 1540 lines
  [LIB] pipeline.py - 2188 lines
  [LIB] random_projection.py - 824 lines
venv/lib/python3.10/site-packages/sklearn/__check_build/
  [LIB] __init__.py - 54 lines
venv/lib/python3.10/site-packages/sklearn/_build_utils/
  [LIB] __init__.py - 0 lines
  [LIB] tempita.py - 62 lines
  [LIB] version.py - 16 lines
venv/lib/python3.10/site-packages/sklearn/_loss/
  [LIB] __init__.py - 33 lines
  [LIB] link.py - 282 lines
  [LIB] loss.py - 1181 lines
venv/lib/python3.10/site-packages/sklearn/_loss/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/cluster/
  [LIB] __init__.py - 56 lines
  [LIB] _affinity_propagation.py - 607 lines
  [LIB] _agglomerative.py - 1333 lines
  [LIB] _bicluster.py - 621 lines
  [LIB] _birch.py - 749 lines
  [LIB] _bisect_k_means.py - 543 lines
  [LIB] _dbscan.py - 480 lines
  [LIB] _feature_agglomeration.py - 76 lines
  [LIB] _kmeans.py - 2303 lines
  [LIB] _mean_shift.py - 579 lines
  [LIB] _optics.py - 1202 lines
  [LIB] _spectral.py - 805 lines
venv/lib/python3.10/site-packages/sklearn/cluster/_hdbscan/
  [LIB] __init__.py - 2 lines
  [LIB] hdbscan.py - 1000 lines
venv/lib/python3.10/site-packages/sklearn/cluster/_hdbscan/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/cluster/tests/
  [LIB] __init__.py - 0 lines
  [LIB] common.py - 37 lines
venv/lib/python3.10/site-packages/sklearn/compose/
  [LIB] __init__.py - 23 lines
  [LIB] _column_transformer.py - 1599 lines
  [LIB] _target.py - 397 lines
venv/lib/python3.10/site-packages/sklearn/compose/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/covariance/
  [LIB] __init__.py - 46 lines
  [LIB] _elliptic_envelope.py - 266 lines
  [LIB] _empirical_covariance.py - 370 lines
  [LIB] _graph_lasso.py - 1145 lines
  [LIB] _robust_covariance.py - 874 lines
  [LIB] _shrunk_covariance.py - 822 lines
venv/lib/python3.10/site-packages/sklearn/covariance/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/cross_decomposition/
  [LIB] __init__.py - 8 lines
  [LIB] _pls.py - 1097 lines
venv/lib/python3.10/site-packages/sklearn/cross_decomposition/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/
  [LIB] __init__.py - 166 lines
  [LIB] _arff_parser.py - 543 lines
  [LIB] _base.py - 1636 lines
  [LIB] _california_housing.py - 248 lines
  [LIB] _covtype.py - 252 lines
  [LIB] _kddcup99.py - 429 lines
  [LIB] _lfw.py - 648 lines
  [LIB] _olivetti_faces.py - 184 lines
  [LIB] _openml.py - 1160 lines
  [LIB] _rcv1.py - 334 lines
  [LIB] _samples_generator.py - 2383 lines
  [LIB] _species_distributions.py - 289 lines
  [LIB] _svmlight_format_io.py - 585 lines
  [LIB] _twenty_newsgroups.py - 625 lines
venv/lib/python3.10/site-packages/sklearn/datasets/data/
  [LIB] __init__.py - 2 lines
venv/lib/python3.10/site-packages/sklearn/datasets/descr/
  [LIB] __init__.py - 2 lines
venv/lib/python3.10/site-packages/sklearn/datasets/images/
  [LIB] __init__.py - 2 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_1/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_1119/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_1590/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_2/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_292/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_3/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_40589/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_40675/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_40945/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_40966/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_42074/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_42585/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_561/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_61/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/datasets/tests/data/openml/id_62/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/decomposition/
  [LIB] __init__.py - 54 lines
  [LIB] _base.py - 202 lines
  [LIB] _dict_learning.py - 2329 lines
  [LIB] _factor_analysis.py - 457 lines
  [LIB] _fastica.py - 804 lines
  [LIB] _incremental_pca.py - 426 lines
  [LIB] _kernel_pca.py - 577 lines
  [LIB] _lda.py - 959 lines
  [LIB] _nmf.py - 2409 lines
  [LIB] _pca.py - 857 lines
  [LIB] _sparse_pca.py - 548 lines
  [LIB] _truncated_svd.py - 322 lines
venv/lib/python3.10/site-packages/sklearn/decomposition/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/ensemble/
  [LIB] __init__.py - 45 lines
  [LIB] _bagging.py - 1480 lines
  [LIB] _base.py - 307 lines
  [LIB] _forest.py - 3045 lines
  [LIB] _gb.py - 2196 lines (ports: 2000)
  [LIB] _iforest.py - 673 lines
  [LIB] _stacking.py - 1145 lines
  [LIB] _voting.py - 734 lines
  [LIB] _weight_boosting.py - 1173 lines
venv/lib/python3.10/site-packages/sklearn/ensemble/_hist_gradient_boosting/
  [LIB] __init__.py - 8 lines
  [LIB] binning.py - 333 lines
  [LIB] gradient_boosting.py - 2371 lines
  [LIB] grower.py - 821 lines
  [LIB] predictor.py - 146 lines
  [LIB] utils.py - 149 lines
venv/lib/python3.10/site-packages/sklearn/ensemble/_hist_gradient_boosting/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/ensemble/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/experimental/
  [LIB] __init__.py - 10 lines
  [LIB] enable_halving_search_cv.py - 35 lines
  [LIB] enable_hist_gradient_boosting.py - 23 lines
  [LIB] enable_iterative_imputer.py - 23 lines
venv/lib/python3.10/site-packages/sklearn/experimental/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/externals/
  [LIB] __init__.py - 5 lines
  [LIB] _arff.py - 1107 lines
  [LIB] _array_api_compat_vendor.py - 5 lines
  [TEST] conftest.py - 6 lines
venv/lib/python3.10/site-packages/sklearn/externals/_packaging/
  [LIB] __init__.py - 0 lines
  [LIB] _structures.py - 90 lines
  [LIB] version.py - 535 lines
venv/lib/python3.10/site-packages/sklearn/externals/_scipy/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/externals/_scipy/sparse/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/externals/_scipy/sparse/csgraph/
  [LIB] __init__.py - 1 lines
  [LIB] _laplacian.py - 557 lines
venv/lib/python3.10/site-packages/sklearn/externals/array_api_compat/
  [LIB] __init__.py - 22 lines
  [LIB] _internal.py - 59 lines
venv/lib/python3.10/site-packages/sklearn/externals/array_api_compat/common/
  [LIB] __init__.py - 1 lines
  [LIB] _aliases.py - 727 lines
  [LIB] _fft.py - 213 lines
  [LIB] _helpers.py - 1058 lines
  [LIB] _linalg.py - 232 lines
  [LIB] _typing.py - 192 lines
venv/lib/python3.10/site-packages/sklearn/externals/array_api_compat/cupy/
  [LIB] __init__.py - 13 lines
  [LIB] _aliases.py - 156 lines
  [LIB] _info.py - 336 lines
  [LIB] _typing.py - 31 lines
  [LIB] fft.py - 36 lines
  [LIB] linalg.py - 49 lines
venv/lib/python3.10/site-packages/sklearn/externals/array_api_compat/dask/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/externals/array_api_compat/dask/array/
  [LIB] __init__.py - 12 lines
  [LIB] _aliases.py - 376 lines
  [LIB] _info.py - 416 lines
  [LIB] fft.py - 21 lines
  [LIB] linalg.py - 72 lines
venv/lib/python3.10/site-packages/sklearn/externals/array_api_compat/numpy/
  [LIB] __init__.py - 28 lines
  [LIB] _aliases.py - 190 lines
  [LIB] _info.py - 366 lines
  [LIB] _typing.py - 30 lines
  [LIB] fft.py - 35 lines
  [LIB] linalg.py - 143 lines
venv/lib/python3.10/site-packages/sklearn/externals/array_api_compat/torch/
  [LIB] __init__.py - 22 lines
  [LIB] _aliases.py - 855 lines
  [LIB] _info.py - 369 lines
  [LIB] _typing.py - 3 lines
  [LIB] fft.py - 85 lines
  [LIB] linalg.py - 121 lines
venv/lib/python3.10/site-packages/sklearn/externals/array_api_extra/
  [LIB] __init__.py - 38 lines
  [LIB] _delegation.py - 172 lines
  [TEST] testing.py - 324 lines
venv/lib/python3.10/site-packages/sklearn/externals/array_api_extra/_lib/
  [LIB] __init__.py - 5 lines
  [LIB] _at.py - 454 lines
  [LIB] _backends.py - 51 lines
  [LIB] _funcs.py - 915 lines
  [LIB] _lazy.py - 352 lines
  [TEST] _testing.py - 220 lines
venv/lib/python3.10/site-packages/sklearn/externals/array_api_extra/_lib/_utils/
  [LIB] __init__.py - 1 lines
  [LIB] _compat.py - 70 lines
  [LIB] _helpers.py - 272 lines
  [LIB] _typing.py - 10 lines
venv/lib/python3.10/site-packages/sklearn/feature_extraction/
  [LIB] __init__.py - 18 lines
  [LIB] _dict_vectorizer.py - 459 lines
  [LIB] _hash.py - 208 lines
  [LIB] _stop_words.py - 328 lines
  [LIB] image.py - 687 lines
  [LIB] text.py - 2136 lines
venv/lib/python3.10/site-packages/sklearn/feature_extraction/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/feature_selection/
  [LIB] __init__.py - 50 lines
  [LIB] _base.py - 267 lines
  [LIB] _from_model.py - 513 lines
  [LIB] _mutual_info.py - 580 lines
  [LIB] _rfe.py - 1025 lines
  [LIB] _sequential.py - 363 lines
  [LIB] _univariate_selection.py - 1171 lines
  [LIB] _variance_threshold.py - 141 lines
venv/lib/python3.10/site-packages/sklearn/feature_selection/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/frozen/
  [LIB] __init__.py - 6 lines
  [LIB] _frozen.py - 166 lines
venv/lib/python3.10/site-packages/sklearn/frozen/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/gaussian_process/
  [LIB] __init__.py - 10 lines
  [LIB] _gpc.py - 973 lines
  [LIB] _gpr.py - 675 lines
  [LIB] kernels.py - 2408 lines
venv/lib/python3.10/site-packages/sklearn/gaussian_process/tests/
  [LIB] __init__.py - 0 lines
  [LIB] _mini_sequence_kernel.py - 54 lines
venv/lib/python3.10/site-packages/sklearn/impute/
  [LIB] __init__.py - 28 lines
  [LIB] _base.py - 1139 lines
  [LIB] _iterative.py - 1030 lines
  [LIB] _knn.py - 411 lines
venv/lib/python3.10/site-packages/sklearn/impute/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/inspection/
  [LIB] __init__.py - 16 lines
  [LIB] _partial_dependence.py - 775 lines
  [LIB] _pd_utils.py - 68 lines
  [LIB] _permutation_importance.py - 313 lines
venv/lib/python3.10/site-packages/sklearn/inspection/_plot/
  [LIB] __init__.py - 2 lines
  [LIB] decision_boundary.py - 564 lines
  [LIB] partial_dependence.py - 1495 lines
venv/lib/python3.10/site-packages/sklearn/inspection/_plot/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/inspection/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/linear_model/
  [LIB] __init__.py - 95 lines
  [LIB] _base.py - 869 lines
  [LIB] _bayes.py - 826 lines
  [LIB] _coordinate_descent.py - 3403 lines
  [LIB] _huber.py - 363 lines
  [LIB] _least_angle.py - 2346 lines
  [LIB] _linear_loss.py - 825 lines
  [LIB] _logistic.py - 2327 lines
  [LIB] _omp.py - 1121 lines
  [LIB] _passive_aggressive.py - 573 lines
  [LIB] _perceptron.py - 226 lines
  [LIB] _quantile.py - 301 lines
  [LIB] _ransac.py - 726 lines
  [LIB] _ridge.py - 2899 lines
  [LIB] _sag.py - 370 lines
  [LIB] _stochastic_gradient.py - 2604 lines
  [LIB] _theil_sen.py - 467 lines
venv/lib/python3.10/site-packages/sklearn/linear_model/_glm/
  [LIB] __init__.py - 16 lines
  [LIB] _newton_solver.py - 618 lines
  [LIB] glm.py - 911 lines
venv/lib/python3.10/site-packages/sklearn/linear_model/_glm/tests/
  [LIB] __init__.py - 2 lines
venv/lib/python3.10/site-packages/sklearn/linear_model/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/manifold/
  [LIB] __init__.py - 22 lines
  [LIB] _isomap.py - 442 lines
  [LIB] _locally_linear.py - 879 lines (ports: 2323,5591)
  [LIB] _mds.py - 714 lines
  [LIB] _spectral_embedding.py - 776 lines
  [LIB] _t_sne.py - 1184 lines (ports: 2579,3221)
venv/lib/python3.10/site-packages/sklearn/manifold/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/metrics/
  [LIB] __init__.py - 181 lines
  [LIB] _base.py - 193 lines
  [LIB] _classification.py - 3730 lines
  [LIB] _ranking.py - 2077 lines
  [LIB] _regression.py - 1930 lines
  [LIB] _scorer.py - 1166 lines
  [LIB] pairwise.py - 2675 lines
venv/lib/python3.10/site-packages/sklearn/metrics/_pairwise_distances_reduction/
  [LIB] __init__.py - 112 lines
  [LIB] _dispatcher.py - 767 lines
venv/lib/python3.10/site-packages/sklearn/metrics/_plot/
  [LIB] __init__.py - 2 lines
  [LIB] confusion_matrix.py - 499 lines
  [LIB] det_curve.py - 371 lines
  [LIB] precision_recall_curve.py - 555 lines
  [LIB] regression.py - 413 lines
  [LIB] roc_curve.py - 795 lines
venv/lib/python3.10/site-packages/sklearn/metrics/_plot/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/metrics/cluster/
  [LIB] __init__.py - 55 lines
  [LIB] _bicluster.py - 114 lines
  [LIB] _supervised.py - 1314 lines
  [LIB] _unsupervised.py - 463 lines
venv/lib/python3.10/site-packages/sklearn/metrics/cluster/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/metrics/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/mixture/
  [LIB] __init__.py - 9 lines
  [LIB] _base.py - 571 lines
  [LIB] _bayesian_mixture.py - 891 lines
  [LIB] _gaussian_mixture.py - 934 lines
venv/lib/python3.10/site-packages/sklearn/mixture/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/model_selection/
  [LIB] __init__.py - 99 lines
  [LIB] _classification_threshold.py - 889 lines
  [LIB] _plot.py - 885 lines
  [LIB] _search.py - 1996 lines
  [LIB] _search_successive_halving.py - 1095 lines
  [LIB] _split.py - 3055 lines
  [LIB] _validation.py - 2530 lines
venv/lib/python3.10/site-packages/sklearn/model_selection/tests/
  [LIB] __init__.py - 0 lines
  [LIB] common.py - 24 lines
venv/lib/python3.10/site-packages/sklearn/neighbors/
  [LIB] __init__.py - 42 lines
  [LIB] _base.py - 1404 lines
  [LIB] _classification.py - 919 lines
  [LIB] _graph.py - 704 lines
  [LIB] _kde.py - 359 lines
  [LIB] _lof.py - 518 lines
  [LIB] _nca.py - 534 lines
  [LIB] _nearest_centroid.py - 359 lines
  [LIB] _regression.py - 513 lines
  [LIB] _unsupervised.py - 179 lines
venv/lib/python3.10/site-packages/sklearn/neighbors/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/neural_network/
  [LIB] __init__.py - 9 lines
  [LIB] _base.py - 287 lines
  [LIB] _multilayer_perceptron.py - 1797 lines
  [LIB] _rbm.py - 445 lines
  [LIB] _stochastic_optimizers.py - 287 lines
venv/lib/python3.10/site-packages/sklearn/neural_network/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/preprocessing/
  [LIB] __init__.py - 63 lines
  [LIB] _data.py - 3706 lines
  [LIB] _discretization.py - 548 lines
  [LIB] _encoders.py - 1698 lines
  [LIB] _function_transformer.py - 446 lines
  [LIB] _label.py - 963 lines
  [LIB] _polynomial.py - 1153 lines
  [LIB] _target_encoder.py - 534 lines
venv/lib/python3.10/site-packages/sklearn/preprocessing/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/semi_supervised/
  [LIB] __init__.py - 13 lines
  [LIB] _label_propagation.py - 630 lines
  [LIB] _self_training.py - 625 lines
venv/lib/python3.10/site-packages/sklearn/semi_supervised/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/svm/
  [LIB] __init__.py - 21 lines
  [LIB] _base.py - 1262 lines
  [LIB] _bounds.py - 98 lines
  [LIB] _classes.py - 1789 lines
venv/lib/python3.10/site-packages/sklearn/svm/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/tests/
  [LIB] __init__.py - 0 lines
  [LIB] metadata_routing_common.py - 584 lines
venv/lib/python3.10/site-packages/sklearn/tree/
  [LIB] __init__.py - 24 lines
  [LIB] _classes.py - 1997 lines
  [LIB] _export.py - 1167 lines
  [LIB] _reingold_tilford.py - 188 lines
venv/lib/python3.10/site-packages/sklearn/tree/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/utils/
  [LIB] __init__.py - 84 lines
  [LIB] _arpack.py - 33 lines
  [LIB] _array_api.py - 1006 lines
  [LIB] _available_if.py - 96 lines
  [LIB] _bunch.py - 70 lines
  [LIB] _chunking.py - 178 lines
  [LIB] _encode.py - 376 lines
  [LIB] _estimator_html_repr.py - 34 lines
  [LIB] _indexing.py - 755 lines
  [LIB] _mask.py - 181 lines
  [LIB] _metadata_requests.py - 1628 lines
  [LIB] _missing.py - 68 lines
  [LIB] _mocking.py - 419 lines
  [LIB] _optional_dependencies.py - 46 lines
  [LIB] _param_validation.py - 910 lines
  [LIB] _plotting.py - 419 lines
  [LIB] _pprint.py - 463 lines
  [LIB] _response.py - 317 lines
  [LIB] _set_output.py - 460 lines
  [LIB] _show_versions.py - 115 lines
  [LIB] _tags.py - 355 lines
  [TEST] _testing.py - 1454 lines
  [LIB] _unique.py - 108 lines
  [LIB] _user_interface.py - 57 lines
  [LIB] class_weight.py - 231 lines
  [LIB] deprecation.py - 149 lines
  [LIB] discovery.py - 255 lines
  [LIB] estimator_checks.py - 5348 lines
  [LIB] extmath.py - 1395 lines
  [LIB] fixes.py - 427 lines
  [LIB] graph.py - 162 lines
  [LIB] metadata_routing.py - 23 lines
  [LIB] metaestimators.py - 163 lines
  [LIB] multiclass.py - 584 lines
  [LIB] optimize.py - 389 lines
  [LIB] parallel.py - 177 lines
  [LIB] random.py - 101 lines
  [LIB] sparsefuncs.py - 742 lines
  [LIB] stats.py - 122 lines
  [LIB] validation.py - 2977 lines
venv/lib/python3.10/site-packages/sklearn/utils/_repr_html/
  [LIB] __init__.py - 2 lines
  [LIB] base.py - 152 lines
  [LIB] estimator.py - 497 lines
  [LIB] params.py - 83 lines
venv/lib/python3.10/site-packages/sklearn/utils/_repr_html/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sklearn/utils/_test_common/
  [LIB] __init__.py - 2 lines
  [LIB] instance_generator.py - 1293 lines
venv/lib/python3.10/site-packages/sklearn/utils/tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sniffio/
  [LIB] __init__.py - 17 lines
  [LIB] _impl.py - 95 lines
  [LIB] _version.py - 3 lines
venv/lib/python3.10/site-packages/sniffio/_tests/
  [LIB] __init__.py - 0 lines
venv/lib/python3.10/site-packages/sqlalchemy/
  [LIB] __init__.py - 283 lines
  [LIB] events.py - 17 lines
  [LIB] exc.py - 832 lines
  [LIB] inspection.py - 174 lines
  [LIB] log.py - 288 lines
  [LIB] schema.py - 71 lines
  [LIB] types.py - 76 lines
venv/lib/python3.10/site-packages/sqlalchemy/connectors/
  [LIB] __init__.py - 18 lines
  [LIB] aioodbc.py - 174 lines
  [LIB] asyncio.py - 213 lines
  [LIB] pyodbc.py - 247 lines
venv/lib/python3.10/site-packages/sqlalchemy/cyextension/
  [LIB] __init__.py - 6 lines
venv/lib/python3.10/site-packages/sqlalchemy/dialects/
  [LIB] __init__.py - 61 lines
  [LIB] _typing.py - 30 lines
venv/lib/python3.10/site-packages/sqlalchemy/dialects/mssql/
  [LIB] __init__.py - 88 lines
  [LIB] aioodbc.py - 63 lines (ports: 1433)
  [LIB] base.py - 4055 lines (ports: 1433)
  [LIB] information_schema.py - 254 lines
  [LIB] json.py - 129 lines
  [LIB] provision.py - 162 lines
  [LIB] pymssql.py - 126 lines
  [LIB] pyodbc.py - 760 lines (ports: 1433)
venv/lib/python3.10/site-packages/sqlalchemy/dialects/mysql/
  [LIB] __init__.py - 104 lines
  [LIB] aiomysql.py - 335 lines
  [LIB] asyncmy.py - 339 lines
  [LIB] base.py - 3581 lines
  [LIB] cymysql.py - 84 lines
  [LIB] dml.py - 225 lines
  [LIB] enumerated.py - 243 lines
  [LIB] expression.py - 143 lines
  [LIB] json.py - 81 lines
  [LIB] mariadb.py - 67 lines
  [LIB] mariadbconnector.py - 277 lines
  [LIB] mysqlconnector.py - 253 lines
  [LIB] mysqldb.py - 305 lines
  [LIB] provision.py - 114 lines
  [LIB] pymysql.py - 136 lines
  [LIB] pyodbc.py - 139 lines (ports: 3307)
  [LIB] reflection.py - 677 lines
  [LIB] reserved_words.py - 571 lines
  [LIB] types.py - 773 lines
venv/lib/python3.10/site-packages/sqlalchemy/dialects/oracle/
  [LIB] __init__.py - 77 lines
  [LIB] base.py - 3747 lines (ports: 1521)
  [LIB] cx_oracle.py - 1552 lines (ports: 1521,4457)
  [LIB] dictionary.py - 507 lines (ports: 2619)
  [LIB] oracledb.py - 947 lines (ports: 1521)
  [LIB] provision.py - 220 lines
  [LIB] types.py - 316 lines
  [LIB] vector.py - 266 lines
venv/lib/python3.10/site-packages/sqlalchemy/dialects/postgresql/
  [LIB] __init__.py - 167 lines
  [LIB] _psycopg_common.py - 186 lines
  [LIB] array.py - 509 lines
  [LIB] asyncpg.py - 1287 lines (ports: 5432)
  [LIB] base.py - 5175 lines (ports: 3000)
  [LIB] dml.py - 339 lines
  [LIB] ext.py - 536 lines
  [LIB] hstore.py - 406 lines
  [LIB] json.py - 367 lines
  [LIB] named_types.py - 538 lines
  [LIB] operators.py - 129 lines
  [LIB] pg8000.py - 666 lines
  [LIB] pg_catalog.py - 312 lines
  [LIB] provision.py - 175 lines
  [LIB] psycopg.py - 783 lines
  [LIB] psycopg2.py - 892 lines (ports: 5432)
  [LIB] psycopg2cffi.py - 61 lines
  [LIB] ranges.py - 1031 lines
  [LIB] types.py - 313 lines
venv/lib/python3.10/site-packages/sqlalchemy/dialects/sqlite/
  [LIB] __init__.py - 57 lines
  [LIB] aiosqlite.py - 398 lines
  [LIB] base.py - 2945 lines (ports: 3633)
  [LIB] dml.py - 263 lines
  [LIB] json.py - 92 lines
  [LIB] provision.py - 196 lines
  [LIB] pysqlcipher.py - 157 lines
  [LIB] pysqlite.py - 705 lines
venv/lib/python3.10/site-packages/sqlalchemy/engine/
  [LIB] __init__.py - 62 lines
  [LIB] _py_processors.py - 136 lines
  [LIB] _py_row.py - 128 lines
  [LIB] _py_util.py - 74 lines
  [LIB] base.py - 3370 lines
  [LIB] characteristics.py - 155 lines
  [LIB] create.py - 878 lines
  [LIB] cursor.py - 2181 lines
  [LIB] default.py - 2380 lines
  [LIB] events.py - 965 lines
  [LIB] interfaces.py - 3413 lines
  [LIB] mock.py - 134 lines
  [LIB] processors.py - 61 lines
  [LIB] reflection.py - 2102 lines
  [LIB] result.py - 2387 lines
  [LIB] row.py - 400 lines
  [LIB] strategies.py - 19 lines
  [LIB] url.py - 924 lines
  [LIB] util.py - 167 lines
venv/lib/python3.10/site-packages/sqlalchemy/event/
  [LIB] __init__.py - 25 lines
  [LIB] api.py - 222 lines
  [LIB] attr.py - 655 lines
  [LIB] base.py - 472 lines
  [LIB] legacy.py - 246 lines
  [LIB] registry.py - 390 lines
venv/lib/python3.10/site-packages/sqlalchemy/ext/
  [LIB] __init__.py - 11 lines
  [LIB] associationproxy.py - 2013 lines
  [LIB] automap.py - 1701 lines
  [LIB] baked.py - 570 lines
  [LIB] compiler.py - 600 lines
  [LIB] horizontal_shard.py - 478 lines
  [LIB] hybrid.py - 1533 lines
  [LIB] indexable.py - 345 lines
  [LIB] instrumentation.py - 450 lines
  [LIB] mutable.py - 1095 lines
  [LIB] orderinglist.py - 427 lines
  [LIB] serializer.py - 185 lines
venv/lib/python3.10/site-packages/sqlalchemy/ext/asyncio/
  [LIB] __init__.py - 25 lines
  [LIB] base.py - 281 lines
  [LIB] engine.py - 1469 lines
  [LIB] exc.py - 21 lines
  [LIB] result.py - 962 lines
  [LIB] scoping.py - 1613 lines
  [LIB] session.py - 1961 lines
venv/lib/python3.10/site-packages/sqlalchemy/ext/declarative/
  [LIB] __init__.py - 65 lines
  [LIB] extensions.py - 564 lines
venv/lib/python3.10/site-packages/sqlalchemy/ext/mypy/
  [LIB] __init__.py - 6 lines
  [LIB] apply.py - 324 lines
  [LIB] decl_class.py - 515 lines
  [LIB] infer.py - 590 lines
  [LIB] names.py - 335 lines
  [LIB] plugin.py - 303 lines
  [LIB] util.py - 357 lines
venv/lib/python3.10/site-packages/sqlalchemy/future/
  [LIB] __init__.py - 16 lines
  [LIB] engine.py - 15 lines
venv/lib/python3.10/site-packages/sqlalchemy/orm/
  [LIB] __init__.py - 170 lines
  [LIB] _orm_constructors.py - 2590 lines
  [LIB] _typing.py - 179 lines
  [LIB] attributes.py - 2835 lines
  [LIB] base.py - 973 lines
  [LIB] bulk_persistence.py - 2123 lines
  [LIB] clsregistry.py - 571 lines (ports: 3208)
  [LIB] collections.py - 1627 lines (ports: 2406)
  [LIB] context.py - 3334 lines
  [LIB] decl_api.py - 1917 lines
  [LIB] decl_base.py - 2186 lines (ports: 1892)
  [LIB] dependency.py - 1304 lines
  [LIB] descriptor_props.py - 1077 lines
  [LIB] dynamic.py - 300 lines
  [LIB] evaluator.py - 379 lines
  [LIB] events.py - 3271 lines
  [LIB] exc.py - 237 lines
  [LIB] identity.py - 302 lines
  [LIB] instrumentation.py - 754 lines (ports: 2362)
  [LIB] interfaces.py - 1490 lines
  [LIB] loading.py - 1682 lines
  [LIB] mapped_collection.py - 557 lines
  [LIB] mapper.py - 4431 lines (ports: 1523,1570)
  [LIB] path_registry.py - 811 lines
  [LIB] persistence.py - 1782 lines (ports: 3801)
  [LIB] properties.py - 884 lines
  [LIB] query.py - 3453 lines
  [LIB] relationships.py - 3509 lines (ports: 2229)
  [LIB] scoping.py - 2162 lines
  [LIB] session.py - 5294 lines
  [LIB] state.py - 1143 lines
  [LIB] state_changes.py - 198 lines
  [LIB] strategies.py - 3470 lines
  [LIB] strategy_options.py - 2549 lines
  [LIB] sync.py - 164 lines
  [LIB] unitofwork.py - 796 lines
  [LIB] util.py - 2403 lines
  [LIB] writeonly.py - 678 lines
venv/lib/python3.10/site-packages/sqlalchemy/pool/
  [LIB] __init__.py - 44 lines
  [LIB] base.py - 1516 lines
  [LIB] events.py - 372 lines
  [LIB] impl.py - 581 lines
venv/lib/python3.10/site-packages/sqlalchemy/sql/
  [LIB] __init__.py - 145 lines
  [LIB] _dml_constructors.py - 132 lines
  [LIB] _elements_constructors.py - 1872 lines
  [LIB] _orm_types.py - 20 lines
  [LIB] _py_util.py - 75 lines
  [LIB] _selectable_constructors.py - 715 lines
  [LIB] _typing.py - 468 lines
  [LIB] annotation.py - 585 lines
  [LIB] base.py - 2197 lines
  [LIB] cache_key.py - 1057 lines
  [LIB] coercions.py - 1403 lines
  [LIB] compiler.py - 7946 lines
  [LIB] crud.py - 1678 lines
  [LIB] ddl.py - 1442 lines
  [LIB] default_comparator.py - 552 lines
  [LIB] dml.py - 1837 lines
  [LIB] elements.py - 5544 lines (ports: 4730)
  [LIB] events.py - 458 lines
  [LIB] expression.py - 162 lines
  [LIB] functions.py - 2106 lines
  [LIB] lambdas.py - 1440 lines
  [LIB] naming.py - 212 lines (ports: 3989)
  [LIB] operators.py - 2623 lines
  [LIB] roles.py - 323 lines
  [LIB] schema.py - 6218 lines
  [LIB] selectable.py - 7193 lines
  [LIB] sqltypes.py - 3921 lines (ports: 3725)
  [LIB] traversals.py - 1024 lines
  [LIB] type_api.py - 2362 lines
  [LIB] util.py - 1487 lines
  [LIB] visitors.py - 1167 lines
venv/lib/python3.10/site-packages/sqlalchemy/testing/
  [LIB] __init__.py - 96 lines
  [LIB] assertions.py - 989 lines
  [LIB] assertsql.py - 516 lines
  [LIB] asyncio.py - 135 lines
  [CONFIG] config.py - 423 lines
  [LIB] engines.py - 474 lines
  [LIB] entities.py - 117 lines
  [LIB] exclusions.py - 435 lines
  [LIB] pickleable.py - 155 lines
  [LIB] profiling.py - 324 lines
  [LIB] provision.py - 502 lines
  [LIB] requirements.py - 1893 lines
  [LIB] schema.py - 224 lines
  [LIB] util.py - 538 lines
  [LIB] warnings.py - 52 lines
venv/lib/python3.10/site-packages/sqlalchemy/testing/fixtures/
  [LIB] __init__.py - 28 lines
  [LIB] base.py - 366 lines
  [LIB] mypy.py - 332 lines
  [LIB] orm.py - 227 lines
  [LIB] sql.py - 503 lines
venv/lib/python3.10/site-packages/sqlalchemy/testing/plugin/
  [LIB] __init__.py - 6 lines
  [LIB] bootstrap.py - 51 lines
  [LIB] plugin_base.py - 779 lines
  [TEST] pytestplugin.py - 867 lines
venv/lib/python3.10/site-packages/sqlalchemy/testing/suite/
  [LIB] __init__.py - 19 lines
venv/lib/python3.10/site-packages/sqlalchemy/util/
  [LIB] __init__.py - 160 lines
  [LIB] _collections.py - 717 lines
  [LIB] _concurrency_py3k.py - 288 lines
  [LIB] _has_cy.py - 40 lines
  [LIB] _py_collections.py - 541 lines
  [LIB] compat.py - 303 lines
  [LIB] concurrency.py - 108 lines
  [LIB] deprecations.py - 401 lines
  [LIB] langhelpers.py - 2303 lines
  [LIB] preloaded.py - 150 lines
  [LIB] queue.py - 322 lines
  [LIB] tool_support.py - 201 lines
  [LIB] topological.py - 120 lines
  [LIB] typing.py - 733 lines
venv/lib/python3.10/site-packages/starlette/
  [LIB] __init__.py - 1 lines
  [LIB] _exception_handler.py - 65 lines
  [LIB] _utils.py - 101 lines
  [LIB] applications.py - 250 lines
  [LIB] authentication.py - 148 lines
  [LIB] background.py - 42 lines
  [LIB] concurrency.py - 63 lines
  [CONFIG] config.py - 139 lines
  [LIB] convertors.py - 89 lines
  [LIB] datastructures.py - 692 lines
  [LIB] endpoints.py - 123 lines
  [LIB] exceptions.py - 33 lines
  [LIB] formparsers.py - 276 lines
  [LIB] requests.py - 323 lines
  [LIB] responses.py - 548 lines
  [LIB] routing.py - 876 lines
  [LIB] schemas.py - 147 lines
  [LIB] staticfiles.py - 220 lines
  [LIB] status.py - 95 lines
  [LIB] templating.py - 217 lines
  [TEST] testclient.py - 745 lines
  [LIB] types.py - 26 lines
  [LIB] websockets.py - 196 lines
venv/lib/python3.10/site-packages/starlette/middleware/
  [LIB] __init__.py - 42 lines
  [LIB] authentication.py - 52 lines
  [LIB] base.py - 235 lines
  [LIB] cors.py - 172 lines
  [LIB] errors.py - 259 lines
  [LIB] exceptions.py - 73 lines
  [LIB] gzip.py - 145 lines
  [LIB] httpsredirect.py - 19 lines
  [LIB] sessions.py - 85 lines
  [LIB] trustedhost.py - 60 lines
  [LIB] wsgi.py - 153 lines
venv/lib/python3.10/site-packages/tomli/
  [LIB] __init__.py - 8 lines
  [LIB] _parser.py - 770 lines
  [LIB] _re.py - 112 lines
  [LIB] _types.py - 10 lines
venv/lib/python3.10/site-packages/typing_inspection/
  [LIB] __init__.py - 0 lines
  [LIB] introspection.py - 587 lines
  [LIB] typing_objects.py - 596 lines
venv/lib/python3.10/site-packages/uvicorn/
  [LIB] __init__.py - 5 lines
  [LIB] __main__.py - 4 lines
  [LIB] _subprocess.py - 84 lines
  [LIB] _types.py - 281 lines
  [CONFIG] config.py - 531 lines
  [LIB] importer.py - 34 lines
  [LIB] logging.py - 117 lines
  [LIB] main.py - 604 lines
  [SVC] server.py - 338 lines
  [LIB] workers.py - 114 lines
venv/lib/python3.10/site-packages/uvicorn/lifespan/
  [LIB] __init__.py - 0 lines
  [LIB] off.py - 17 lines
  [LIB] on.py - 137 lines
venv/lib/python3.10/site-packages/uvicorn/loops/
  [LIB] __init__.py - 0 lines
  [LIB] asyncio.py - 10 lines
  [LIB] auto.py - 11 lines
  [LIB] uvloop.py - 7 lines
venv/lib/python3.10/site-packages/uvicorn/middleware/
  [LIB] __init__.py - 0 lines
  [LIB] asgi2.py - 15 lines
  [LIB] message_logger.py - 87 lines
  [LIB] proxy_headers.py - 142 lines
  [LIB] wsgi.py - 199 lines
venv/lib/python3.10/site-packages/uvicorn/protocols/
  [LIB] __init__.py - 0 lines
  [LIB] utils.py - 56 lines
venv/lib/python3.10/site-packages/uvicorn/protocols/http/
  [LIB] __init__.py - 0 lines
  [LIB] auto.py - 15 lines
  [LIB] flow_control.py - 54 lines
  [LIB] h11_impl.py - 543 lines
  [LIB] httptools_impl.py - 570 lines
venv/lib/python3.10/site-packages/uvicorn/protocols/websockets/
  [LIB] __init__.py - 0 lines
  [LIB] auto.py - 21 lines
  [LIB] websockets_impl.py - 387 lines
  [LIB] websockets_sansio_impl.py - 417 lines
  [LIB] wsproto_impl.py - 377 lines
venv/lib/python3.10/site-packages/uvicorn/supervisors/
  [LIB] __init__.py - 16 lines
  [LIB] basereload.py - 126 lines
  [LIB] multiprocess.py - 222 lines
  [LIB] statreload.py - 53 lines
  [LIB] watchfilesreload.py - 85 lines
venv/lib/python3.10/site-packages/websockets/
  [LIB] __init__.py - 236 lines
  [LIB] __main__.py - 5 lines
  [LIB] auth.py - 18 lines
  [LIB] cli.py - 178 lines
  [LIB] client.py - 389 lines
  [LIB] connection.py - 12 lines
  [LIB] datastructures.py - 187 lines
  [LIB] exceptions.py - 473 lines
  [LIB] frames.py - 430 lines
  [LIB] headers.py - 586 lines
  [LIB] http.py - 20 lines
  [LIB] http11.py - 427 lines
  [LIB] imports.py - 100 lines
  [LIB] protocol.py - 758 lines
  [SVC] server.py - 587 lines
  [LIB] streams.py - 151 lines
  [LIB] typing.py - 74 lines
  [LIB] uri.py - 225 lines
  [LIB] utils.py - 51 lines
  [LIB] version.py - 92 lines
venv/lib/python3.10/site-packages/websockets/asyncio/
  [LIB] __init__.py - 0 lines
  [LIB] async_timeout.py - 282 lines
  [LIB] client.py - 820 lines
  [LIB] compatibility.py - 30 lines
  [LIB] connection.py - 1237 lines
  [LIB] messages.py - 314 lines
  [LIB] router.py - 198 lines
  [SVC] server.py - 981 lines
venv/lib/python3.10/site-packages/websockets/extensions/
  [LIB] __init__.py - 4 lines
  [LIB] base.py - 123 lines
  [LIB] permessage_deflate.py - 697 lines
venv/lib/python3.10/site-packages/websockets/legacy/
  [LIB] __init__.py - 11 lines
  [LIB] auth.py - 190 lines
  [LIB] client.py - 705 lines
  [LIB] exceptions.py - 71 lines
  [LIB] framing.py - 225 lines
  [LIB] handshake.py - 158 lines
  [LIB] http.py - 201 lines
  [LIB] protocol.py - 1641 lines
  [SVC] server.py - 1191 lines
venv/lib/python3.10/site-packages/websockets/sync/
  [LIB] __init__.py - 0 lines
  [LIB] client.py - 648 lines
  [LIB] connection.py - 1072 lines
  [LIB] messages.py - 345 lines
  [LIB] router.py - 192 lines
  [SVC] server.py - 763 lines
  [LIB] utils.py - 45 lines
venv/lib/python3.10/site-packages/yaml/
  [LIB] __init__.py - 390 lines
  [LIB] composer.py - 139 lines
  [LIB] constructor.py - 748 lines
  [LIB] cyaml.py - 101 lines
  [LIB] dumper.py - 62 lines
  [LIB] emitter.py - 1137 lines
  [LIB] error.py - 75 lines
  [LIB] events.py - 86 lines
  [LIB] loader.py - 63 lines
  [LIB] nodes.py - 49 lines
  [LIB] parser.py - 589 lines
  [LIB] reader.py - 185 lines
  [LIB] representer.py - 389 lines
  [LIB] resolver.py - 227 lines
  [LIB] scanner.py - 1435 lines
  [LIB] serializer.py - 111 lines
  [LIB] tokens.py - 104 lines
venv/lib/python3.10/site-packages/yarl/
  [LIB] __init__.py - 14 lines
  [LIB] _parse.py - 203 lines
  [LIB] _path.py - 41 lines
  [LIB] _query.py - 114 lines
  [LIB] _quoters.py - 33 lines
  [LIB] _quoting.py - 19 lines
  [LIB] _quoting_py.py - 213 lines
  [LIB] _url.py - 1604 lines (ports: 8080,8329,8443)
windows/bridge_installation/
  [LIB] bridge.py - 676 lines (ports: 8765,11098)
  [LIB] file_access_api.py - 358 lines
windows/bridge_installation/venv/Lib/site-packages/
  [LIB] typing_extensions.py - 4244 lines
windows/bridge_installation/venv/Lib/site-packages/anyio/
  [LIB] __init__.py - 85 lines
  [LIB] from_thread.py - 527 lines
  [LIB] lowlevel.py - 161 lines
  [TEST] pytest_plugin.py - 272 lines
  [LIB] to_interpreter.py - 218 lines
  [LIB] to_process.py - 258 lines
  [LIB] to_thread.py - 69 lines
windows/bridge_installation/venv/Lib/site-packages/anyio/_backends/
  [LIB] __init__.py - 0 lines
  [LIB] _asyncio.py - 2816 lines
  [LIB] _trio.py - 1334 lines
windows/bridge_installation/venv/Lib/site-packages/anyio/_core/
  [LIB] __init__.py - 0 lines
  [LIB] _asyncio_selector_thread.py - 167 lines
  [LIB] _eventloop.py - 166 lines
  [LIB] _exceptions.py - 126 lines
  [LIB] _fileio.py - 742 lines
  [LIB] _resources.py - 18 lines
  [LIB] _signals.py - 27 lines
  [LIB] _sockets.py - 792 lines
  [LIB] _streams.py - 52 lines
  [LIB] _subprocesses.py - 202 lines
  [LIB] _synchronization.py - 732 lines
  [LIB] _tasks.py - 158 lines
  [LIB] _tempfile.py - 616 lines
  [TEST] _testing.py - 78 lines
  [LIB] _typedattr.py - 81 lines
windows/bridge_installation/venv/Lib/site-packages/anyio/abc/
  [LIB] __init__.py - 55 lines
  [LIB] _eventloop.py - 376 lines
  [LIB] _resources.py - 33 lines
  [LIB] _sockets.py - 194 lines
  [LIB] _streams.py - 203 lines
  [LIB] _subprocesses.py - 79 lines
  [LIB] _tasks.py - 101 lines
  [TEST] _testing.py - 65 lines
windows/bridge_installation/venv/Lib/site-packages/anyio/streams/
  [LIB] __init__.py - 0 lines
  [LIB] buffered.py - 119 lines
  [LIB] file.py - 148 lines
  [LIB] memory.py - 317 lines
  [LIB] stapled.py - 141 lines
  [LIB] text.py - 147 lines
  [LIB] tls.py - 352 lines
windows/bridge_installation/venv/Lib/site-packages/certifi/
  [LIB] __init__.py - 4 lines
  [LIB] __main__.py - 12 lines
  [LIB] core.py - 83 lines
windows/bridge_installation/venv/Lib/site-packages/charset_normalizer/
  [LIB] __init__.py - 48 lines
  [LIB] __main__.py - 6 lines
  [LIB] api.py - 668 lines
  [LIB] cd.py - 395 lines
  [LIB] constant.py - 2015 lines
  [LIB] legacy.py - 64 lines
  [LIB] md.py - 635 lines
  [LIB] models.py - 360 lines (ports: 8192)
  [LIB] utils.py - 414 lines
  [LIB] version.py - 8 lines
windows/bridge_installation/venv/Lib/site-packages/charset_normalizer/cli/
  [LIB] __init__.py - 8 lines
  [LIB] __main__.py - 381 lines
windows/bridge_installation/venv/Lib/site-packages/click/
  [LIB] __init__.py - 123 lines
  [LIB] _compat.py - 622 lines
  [LIB] _termui_impl.py - 839 lines
  [LIB] _textwrap.py - 51 lines
  [LIB] _winconsole.py - 296 lines
  [LIB] core.py - 3135 lines
  [LIB] decorators.py - 551 lines
  [LIB] exceptions.py - 308 lines
  [LIB] formatting.py - 301 lines
  [LIB] globals.py - 67 lines
  [LIB] parser.py - 532 lines
  [LIB] shell_completion.py - 644 lines
  [LIB] termui.py - 877 lines
  [TEST] testing.py - 565 lines
  [LIB] types.py - 1165 lines
  [LIB] utils.py - 627 lines
windows/bridge_installation/venv/Lib/site-packages/colorama/
  [LIB] __init__.py - 7 lines
  [LIB] ansi.py - 102 lines
  [LIB] ansitowin32.py - 277 lines
  [LIB] initialise.py - 121 lines
  [LIB] win32.py - 180 lines
  [LIB] winterm.py - 195 lines
windows/bridge_installation/venv/Lib/site-packages/colorama/tests/
  [LIB] __init__.py - 1 lines
  [TEST] ansi_test.py - 76 lines
  [TEST] ansitowin32_test.py - 294 lines
  [TEST] initialise_test.py - 189 lines
  [TEST] isatty_test.py - 57 lines
  [LIB] utils.py - 49 lines
  [TEST] winterm_test.py - 131 lines
windows/bridge_installation/venv/Lib/site-packages/fastapi/
  [LIB] __init__.py - 25 lines
  [LIB] applications.py - 910 lines
  [LIB] background.py - 1 lines
  [LIB] concurrency.py - 40 lines
  [LIB] datastructures.py - 56 lines
  [LIB] encoders.py - 171 lines
  [LIB] exception_handlers.py - 25 lines
  [LIB] exceptions.py - 37 lines
  [LIB] logger.py - 3 lines
  [LIB] param_functions.py - 290 lines
  [LIB] params.py - 381 lines
  [LIB] requests.py - 2 lines
  [LIB] responses.py - 36 lines
  [LIB] routing.py - 1289 lines
  [LIB] staticfiles.py - 1 lines
  [LIB] templating.py - 1 lines
  [TEST] testclient.py - 1 lines
  [LIB] types.py - 3 lines
  [LIB] utils.py - 204 lines
  [LIB] websockets.py - 3 lines
windows/bridge_installation/venv/Lib/site-packages/fastapi/dependencies/
  [LIB] __init__.py - 0 lines
  [LIB] models.py - 58 lines
  [LIB] utils.py - 845 lines
windows/bridge_installation/venv/Lib/site-packages/fastapi/middleware/
  [LIB] __init__.py - 1 lines
  [LIB] asyncexitstack.py - 28 lines
  [LIB] cors.py - 1 lines
  [LIB] gzip.py - 1 lines
  [LIB] httpsredirect.py - 3 lines
  [LIB] trustedhost.py - 3 lines
  [LIB] wsgi.py - 1 lines
windows/bridge_installation/venv/Lib/site-packages/fastapi/openapi/
  [LIB] __init__.py - 0 lines
  [LIB] constants.py - 2 lines
  [LIB] docs.py - 203 lines
  [LIB] models.py - 406 lines
  [LIB] utils.py - 448 lines
windows/bridge_installation/venv/Lib/site-packages/fastapi/security/
  [LIB] __init__.py - 15 lines
  [LIB] api_key.py - 92 lines
  [LIB] base.py - 6 lines
  [LIB] http.py - 165 lines
  [LIB] oauth2.py - 220 lines
  [LIB] open_id_connect_url.py - 34 lines
  [LIB] utils.py - 10 lines
windows/bridge_installation/venv/Lib/site-packages/h11/
  [LIB] __init__.py - 62 lines
  [LIB] _abnf.py - 132 lines
  [LIB] _connection.py - 659 lines
  [LIB] _events.py - 369 lines
  [LIB] _headers.py - 282 lines
  [LIB] _readers.py - 250 lines
  [LIB] _receivebuffer.py - 153 lines
  [LIB] _state.py - 365 lines
  [LIB] _util.py - 135 lines
  [LIB] _version.py - 16 lines
  [LIB] _writers.py - 145 lines
windows/bridge_installation/venv/Lib/site-packages/idna/
  [LIB] __init__.py - 45 lines
  [LIB] codec.py - 122 lines
  [LIB] compat.py - 15 lines
  [LIB] core.py - 437 lines
  [LIB] idnadata.py - 4243 lines
  [LIB] intranges.py - 57 lines
  [LIB] package_data.py - 1 lines
  [LIB] uts46data.py - 8681 lines
windows/bridge_installation/venv/Lib/site-packages/multipart/
  [LIB] __init__.py - 15 lines
  [LIB] decoders.py - 171 lines
  [LIB] exceptions.py - 46 lines
  [LIB] multipart.py - 1893 lines
windows/bridge_installation/venv/Lib/site-packages/multipart/tests/
  [LIB] __init__.py - 0 lines
  [LIB] compat.py - 133 lines
windows/bridge_installation/venv/Lib/site-packages/pip/
  [LIB] __init__.py - 13 lines
  [LIB] __main__.py - 24 lines
  [LIB] __pip-runner__.py - 50 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/
  [LIB] __init__.py - 18 lines
  [LIB] build_env.py - 325 lines
  [LIB] cache.py - 289 lines
  [CONFIG] configuration.py - 383 lines
  [LIB] exceptions.py - 862 lines
  [LIB] main.py - 12 lines
  [LIB] pyproject.py - 185 lines
  [LIB] self_outdated_check.py - 252 lines
  [LIB] wheel_builder.py - 332 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/cli/
  [LIB] __init__.py - 3 lines
  [LIB] autocompletion.py - 175 lines
  [LIB] base_command.py - 233 lines
  [LIB] cmdoptions.py - 1133 lines
  [LIB] command_context.py - 27 lines
  [LIB] index_command.py - 173 lines
  [LIB] main.py - 79 lines
  [LIB] main_parser.py - 133 lines
  [LIB] parser.py - 294 lines
  [LIB] progress_bars.py - 144 lines
  [LIB] req_command.py - 347 lines
  [LIB] spinners.py - 159 lines
  [LIB] status_codes.py - 6 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/commands/
  [LIB] __init__.py - 137 lines
  [LIB] cache.py - 228 lines
  [LIB] check.py - 67 lines
  [LIB] completion.py - 136 lines
  [CONFIG] configuration.py - 280 lines
  [LIB] debug.py - 201 lines
  [LIB] download.py - 146 lines
  [LIB] freeze.py - 108 lines
  [LIB] hash.py - 59 lines
  [LIB] help.py - 41 lines
  [LIB] index.py - 153 lines
  [LIB] inspect.py - 92 lines
  [LIB] install.py - 793 lines
  [LIB] list.py - 391 lines
  [LIB] lock.py - 171 lines
  [LIB] search.py - 176 lines
  [LIB] show.py - 228 lines
  [LIB] uninstall.py - 114 lines
  [LIB] wheel.py - 182 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/distributions/
  [LIB] __init__.py - 21 lines
  [LIB] base.py - 53 lines
  [LIB] installed.py - 29 lines
  [LIB] sdist.py - 158 lines
  [LIB] wheel.py - 42 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/index/
  [LIB] __init__.py - 1 lines
  [LIB] collector.py - 494 lines
  [LIB] package_finder.py - 1050 lines
  [LIB] sources.py - 284 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/locations/
  [LIB] __init__.py - 439 lines
  [LIB] _distutils.py - 172 lines
  [CONFIG] _sysconfig.py - 214 lines
  [LIB] base.py - 81 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/metadata/
  [LIB] __init__.py - 162 lines
  [LIB] _json.py - 86 lines
  [LIB] base.py - 690 lines
  [LIB] pkg_resources.py - 301 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/metadata/importlib/
  [LIB] __init__.py - 6 lines
  [LIB] _compat.py - 85 lines
  [LIB] _dists.py - 228 lines
  [LIB] _envs.py - 140 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/models/
  [LIB] __init__.py - 1 lines
  [LIB] candidate.py - 25 lines
  [LIB] direct_url.py - 224 lines
  [LIB] format_control.py - 78 lines
  [LIB] index.py - 28 lines
  [LIB] installation_report.py - 56 lines
  [LIB] link.py - 608 lines
  [LIB] pylock.py - 183 lines
  [LIB] scheme.py - 25 lines
  [LIB] search_scope.py - 127 lines
  [LIB] selection_prefs.py - 53 lines
  [LIB] target_python.py - 121 lines
  [LIB] wheel.py - 139 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/network/
  [LIB] __init__.py - 1 lines
  [LIB] auth.py - 566 lines
  [LIB] cache.py - 117 lines
  [LIB] download.py - 314 lines
  [LIB] lazy_wheel.py - 210 lines
  [LIB] session.py - 523 lines
  [LIB] utils.py - 98 lines
  [LIB] xmlrpc.py - 61 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/operations/
  [LIB] __init__.py - 0 lines
  [LIB] check.py - 180 lines
  [LIB] freeze.py - 256 lines
  [LIB] prepare.py - 737 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/operations/build/
  [LIB] __init__.py - 0 lines
  [LIB] build_tracker.py - 138 lines
  [LIB] metadata.py - 38 lines
  [LIB] metadata_editable.py - 41 lines
  [LIB] metadata_legacy.py - 73 lines
  [LIB] wheel.py - 37 lines
  [LIB] wheel_editable.py - 46 lines
  [LIB] wheel_legacy.py - 118 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/operations/install/
  [LIB] __init__.py - 1 lines
  [LIB] editable_legacy.py - 46 lines
  [LIB] wheel.py - 738 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/req/
  [LIB] __init__.py - 103 lines
  [LIB] constructors.py - 560 lines
  [LIB] req_dependency_group.py - 79 lines
  [LIB] req_file.py - 623 lines
  [LIB] req_install.py - 934 lines
  [LIB] req_set.py - 82 lines
  [LIB] req_uninstall.py - 636 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/resolution/
  [LIB] __init__.py - 0 lines
  [LIB] base.py - 20 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/resolution/legacy/
  [LIB] __init__.py - 0 lines
  [LIB] resolver.py - 597 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/resolution/resolvelib/
  [LIB] __init__.py - 0 lines
  [LIB] base.py - 139 lines
  [LIB] candidates.py - 579 lines
  [LIB] factory.py - 823 lines
  [LIB] found_candidates.py - 164 lines
  [LIB] provider.py - 281 lines
  [LIB] reporter.py - 83 lines
  [LIB] requirements.py - 245 lines
  [LIB] resolver.py - 320 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/utils/
  [LIB] __init__.py - 0 lines
  [LIB] _jaraco_text.py - 109 lines
  [LIB] _log.py - 38 lines
  [LIB] appdirs.py - 53 lines
  [LIB] compat.py - 79 lines
  [LIB] compatibility_tags.py - 200 lines
  [LIB] datetime.py - 10 lines
  [LIB] deprecation.py - 124 lines
  [LIB] direct_url_helpers.py - 87 lines
  [LIB] egg_link.py - 80 lines
  [LIB] entrypoints.py - 87 lines
  [LIB] filesystem.py - 149 lines
  [LIB] filetypes.py - 26 lines
  [LIB] glibc.py - 101 lines
  [LIB] hashes.py - 147 lines
  [LIB] logging.py - 361 lines
  [LIB] misc.py - 773 lines
  [LIB] packaging.py - 43 lines
  [LIB] retry.py - 42 lines
  [LIB] setuptools_build.py - 147 lines
  [LIB] subprocess.py - 245 lines
  [LIB] temp_dir.py - 296 lines
  [LIB] unpacking.py - 335 lines
  [LIB] urls.py - 55 lines
  [LIB] virtualenv.py - 104 lines
  [LIB] wheel.py - 133 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_internal/vcs/
  [LIB] __init__.py - 15 lines
  [LIB] bazaar.py - 112 lines
  [LIB] git.py - 536 lines
  [LIB] mercurial.py - 163 lines
  [LIB] subversion.py - 324 lines
  [LIB] versioncontrol.py - 688 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/
  [LIB] __init__.py - 117 lines
  [LIB] typing_extensions.py - 4584 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/cachecontrol/
  [LIB] __init__.py - 29 lines
  [LIB] _cmd.py - 70 lines
  [LIB] adapter.py - 168 lines
  [LIB] cache.py - 75 lines
  [LIB] controller.py - 511 lines
  [LIB] filewrapper.py - 119 lines
  [LIB] heuristics.py - 157 lines
  [LIB] serialize.py - 146 lines
  [LIB] wrapper.py - 43 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/cachecontrol/caches/
  [LIB] __init__.py - 8 lines
  [LIB] file_cache.py - 145 lines
  [LIB] redis_cache.py - 48 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/certifi/
  [LIB] __init__.py - 4 lines
  [LIB] __main__.py - 12 lines
  [LIB] core.py - 114 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/dependency_groups/
  [LIB] __init__.py - 13 lines
  [LIB] __main__.py - 65 lines
  [LIB] _implementation.py - 209 lines
  [LIB] _lint_dependency_groups.py - 59 lines
  [LIB] _pip_wrapper.py - 62 lines
  [LIB] _toml_compat.py - 9 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/distlib/
  [LIB] __init__.py - 33 lines
  [LIB] compat.py - 1137 lines
  [LIB] database.py - 1329 lines
  [LIB] index.py - 508 lines
  [LIB] locators.py - 1295 lines
  [LIB] manifest.py - 384 lines
  [LIB] markers.py - 162 lines
  [LIB] metadata.py - 1031 lines
  [LIB] resources.py - 358 lines
  [EXEC] scripts.py - 447 lines
  [LIB] util.py - 1984 lines
  [LIB] version.py - 750 lines
  [LIB] wheel.py - 1100 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/distro/
  [LIB] __init__.py - 54 lines
  [LIB] __main__.py - 4 lines
  [LIB] distro.py - 1403 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/idna/
  [LIB] __init__.py - 45 lines
  [LIB] codec.py - 122 lines
  [LIB] compat.py - 15 lines
  [LIB] core.py - 437 lines
  [LIB] idnadata.py - 4243 lines
  [LIB] intranges.py - 57 lines
  [LIB] package_data.py - 1 lines
  [LIB] uts46data.py - 8681 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/msgpack/
  [LIB] __init__.py - 55 lines
  [LIB] exceptions.py - 48 lines
  [LIB] ext.py - 170 lines
  [LIB] fallback.py - 929 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/packaging/
  [LIB] __init__.py - 15 lines
  [LIB] _elffile.py - 109 lines
  [LIB] _manylinux.py - 262 lines
  [LIB] _musllinux.py - 85 lines
  [LIB] _parser.py - 353 lines
  [LIB] _structures.py - 61 lines
  [LIB] _tokenizer.py - 195 lines
  [LIB] markers.py - 362 lines
  [LIB] metadata.py - 862 lines
  [LIB] requirements.py - 91 lines
  [LIB] specifiers.py - 1019 lines
  [LIB] tags.py - 656 lines
  [LIB] utils.py - 163 lines
  [LIB] version.py - 582 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/packaging/licenses/
  [LIB] __init__.py - 145 lines
  [LIB] _spdx.py - 759 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/pkg_resources/
  [LIB] __init__.py - 3676 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/platformdirs/
  [LIB] __init__.py - 631 lines
  [LIB] __main__.py - 55 lines
  [LIB] android.py - 249 lines
  [LIB] api.py - 299 lines
  [LIB] macos.py - 144 lines
  [LIB] unix.py - 272 lines
  [LIB] version.py - 21 lines
  [LIB] windows.py - 272 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/pygments/
  [LIB] __init__.py - 82 lines
  [LIB] __main__.py - 17 lines
  [LIB] console.py - 70 lines
  [LIB] filter.py - 70 lines
  [LIB] formatter.py - 129 lines
  [LIB] lexer.py - 963 lines (ports: 1024)
  [LIB] modeline.py - 43 lines
  [LIB] plugin.py - 72 lines
  [LIB] regexopt.py - 91 lines
  [LIB] scanner.py - 104 lines
  [LIB] sphinxext.py - 247 lines
  [LIB] style.py - 203 lines
  [LIB] token.py - 214 lines
  [EXEC] unistring.py - 153 lines
  [LIB] util.py - 324 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/pygments/filters/
  [LIB] __init__.py - 940 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/pygments/formatters/
  [LIB] __init__.py - 157 lines
  [LIB] _mapping.py - 23 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/pygments/lexers/
  [LIB] __init__.py - 362 lines
  [LIB] _mapping.py - 602 lines
  [LIB] python.py - 1201 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/pygments/styles/
  [LIB] __init__.py - 61 lines
  [LIB] _mapping.py - 54 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/pyproject_hooks/
  [LIB] __init__.py - 31 lines
  [LIB] _impl.py - 410 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/pyproject_hooks/_in_process/
  [LIB] __init__.py - 21 lines
  [LIB] _in_process.py - 389 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/requests/
  [LIB] __init__.py - 179 lines
  [LIB] __version__.py - 14 lines
  [LIB] _internal_utils.py - 50 lines
  [LIB] adapters.py - 719 lines
  [LIB] api.py - 157 lines
  [LIB] auth.py - 314 lines
  [LIB] certs.py - 17 lines
  [LIB] compat.py - 78 lines
  [LIB] cookies.py - 561 lines
  [LIB] exceptions.py - 151 lines
  [LIB] help.py - 127 lines
  [LIB] hooks.py - 33 lines
  [LIB] models.py - 1037 lines
  [LIB] packages.py - 25 lines
  [LIB] sessions.py - 831 lines (ports: 3128,4012)
  [LIB] status_codes.py - 128 lines
  [LIB] structures.py - 99 lines
  [LIB] utils.py - 1096 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/resolvelib/
  [LIB] __init__.py - 27 lines
  [LIB] providers.py - 196 lines
  [LIB] reporters.py - 55 lines
  [LIB] structs.py - 209 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/resolvelib/resolvers/
  [LIB] __init__.py - 27 lines
  [LIB] abstract.py - 47 lines
  [LIB] criterion.py - 48 lines
  [LIB] exceptions.py - 57 lines
  [LIB] resolution.py - 541 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/rich/
  [LIB] __init__.py - 177 lines
  [LIB] __main__.py - 273 lines
  [LIB] _cell_widths.py - 454 lines
  [LIB] _emoji_codes.py - 3610 lines
  [LIB] _emoji_replace.py - 32 lines
  [LIB] _export_format.py - 76 lines
  [LIB] _extension.py - 10 lines
  [LIB] _fileno.py - 24 lines
  [LIB] _inspect.py - 268 lines
  [LIB] _log_render.py - 94 lines
  [LIB] _loop.py - 43 lines
  [LIB] _null_file.py - 69 lines
  [LIB] _palettes.py - 309 lines
  [LIB] _pick.py - 17 lines
  [LIB] _ratio.py - 159 lines
  [LIB] _spinners.py - 482 lines
  [LIB] _stack.py - 16 lines
  [LIB] _timer.py - 19 lines
  [LIB] _win32_console.py - 661 lines
  [LIB] _windows.py - 71 lines
  [LIB] _windows_renderer.py - 56 lines
  [LIB] _wrap.py - 93 lines
  [LIB] abc.py - 33 lines
  [LIB] align.py - 312 lines
  [LIB] ansi.py - 241 lines
  [LIB] bar.py - 93 lines
  [LIB] box.py - 480 lines
  [LIB] cells.py - 174 lines
  [LIB] color.py - 621 lines
  [LIB] color_triplet.py - 38 lines
  [LIB] columns.py - 187 lines
  [LIB] console.py - 2675 lines
  [LIB] constrain.py - 37 lines
  [LIB] containers.py - 167 lines
  [LIB] control.py - 225 lines
  [LIB] default_styles.py - 193 lines
  [LIB] diagnose.py - 38 lines
  [LIB] emoji.py - 96 lines
  [LIB] errors.py - 34 lines
  [LIB] file_proxy.py - 57 lines
  [LIB] filesize.py - 88 lines
  [LIB] highlighter.py - 232 lines (ports: 7334)
  [LIB] json.py - 139 lines
  [LIB] jupyter.py - 101 lines
  [LIB] layout.py - 442 lines
  [LIB] live.py - 375 lines
  [LIB] live_render.py - 112 lines
  [LIB] logging.py - 297 lines (ports: 8080)
  [LIB] markup.py - 251 lines
  [LIB] measure.py - 151 lines
  [LIB] padding.py - 141 lines
  [LIB] pager.py - 34 lines
  [LIB] palette.py - 100 lines
  [LIB] panel.py - 318 lines
  [LIB] pretty.py - 1016 lines
  [LIB] progress.py - 1715 lines
  [LIB] progress_bar.py - 223 lines
  [LIB] prompt.py - 400 lines
  [LIB] protocol.py - 42 lines
  [LIB] region.py - 10 lines
  [LIB] repr.py - 149 lines
  [LIB] rule.py - 130 lines
  [LIB] scope.py - 86 lines
  [LIB] screen.py - 54 lines
  [LIB] segment.py - 752 lines
  [LIB] spinner.py - 138 lines
  [LIB] status.py - 131 lines
  [LIB] style.py - 796 lines
  [LIB] styled.py - 42 lines
  [LIB] syntax.py - 966 lines
  [LIB] table.py - 1006 lines
  [LIB] terminal_theme.py - 153 lines
  [LIB] text.py - 1361 lines
  [LIB] theme.py - 115 lines
  [LIB] themes.py - 5 lines
  [LIB] traceback.py - 884 lines
  [LIB] tree.py - 257 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/tomli/
  [LIB] __init__.py - 8 lines
  [LIB] _parser.py - 770 lines
  [LIB] _re.py - 112 lines
  [LIB] _types.py - 10 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/tomli_w/
  [LIB] __init__.py - 4 lines
  [LIB] _writer.py - 229 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/truststore/
  [LIB] __init__.py - 36 lines
  [LIB] _api.py - 333 lines
  [LIB] _macos.py - 571 lines
  [LIB] _openssl.py - 66 lines
  [LIB] _ssl_constants.py - 31 lines
  [LIB] _windows.py - 567 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/urllib3/
  [LIB] __init__.py - 102 lines
  [LIB] _collections.py - 355 lines
  [LIB] _version.py - 2 lines
  [LIB] connection.py - 572 lines
  [LIB] connectionpool.py - 1140 lines
  [LIB] exceptions.py - 323 lines (ports: 8080)
  [LIB] fields.py - 274 lines
  [LIB] filepost.py - 98 lines
  [LIB] poolmanager.py - 540 lines (ports: 3128)
  [LIB] request.py - 191 lines
  [LIB] response.py - 879 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/urllib3/contrib/
  [LIB] __init__.py - 0 lines
  [LIB] _appengine_environ.py - 36 lines
  [LIB] appengine.py - 314 lines
  [LIB] ntlmpool.py - 130 lines
  [LIB] pyopenssl.py - 518 lines
  [LIB] securetransport.py - 920 lines
  [LIB] socks.py - 216 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/urllib3/contrib/_securetransport/
  [LIB] __init__.py - 0 lines
  [LIB] bindings.py - 519 lines
  [LIB] low_level.py - 397 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/urllib3/packages/
  [LIB] __init__.py - 0 lines
  [LIB] six.py - 1076 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/urllib3/packages/backports/
  [LIB] __init__.py - 0 lines
  [LIB] makefile.py - 51 lines
  [LIB] weakref_finalize.py - 155 lines
windows/bridge_installation/venv/Lib/site-packages/pip/_vendor/urllib3/util/
  [LIB] __init__.py - 49 lines
  [LIB] connection.py - 149 lines
  [LIB] proxy.py - 57 lines
  [LIB] queue.py - 22 lines
  [LIB] request.py - 137 lines
  [LIB] response.py - 107 lines
  [LIB] retry.py - 622 lines
  [LIB] ssl_.py - 504 lines
  [LIB] ssl_match_hostname.py - 159 lines
  [LIB] ssltransport.py - 221 lines
  [LIB] timeout.py - 271 lines
  [LIB] url.py - 435 lines
  [LIB] wait.py - 152 lines
windows/bridge_installation/venv/Lib/site-packages/pydantic/
  [LIB] __init__.py - 131 lines
  [LIB] _hypothesis_plugin.py - 391 lines
  [LIB] annotated_types.py - 72 lines
  [LIB] class_validators.py - 361 lines
  [LIB] color.py - 494 lines
  [CONFIG] config.py - 191 lines
  [LIB] dataclasses.py - 500 lines
  [LIB] datetime_parse.py - 248 lines
  [LIB] decorator.py - 264 lines
  [LIB] env_settings.py - 350 lines
  [LIB] error_wrappers.py - 161 lines
  [LIB] errors.py - 646 lines
  [LIB] fields.py - 1253 lines
  [LIB] generics.py - 400 lines
  [LIB] json.py - 112 lines
  [LIB] main.py - 1113 lines
  [LIB] mypy.py - 949 lines
  [LIB] networks.py - 747 lines
  [LIB] parse.py - 66 lines
  [LIB] schema.py - 1163 lines
  [LIB] tools.py - 92 lines
  [LIB] types.py - 1205 lines
  [LIB] typing.py - 614 lines
  [LIB] utils.py - 806 lines
  [LIB] validators.py - 768 lines
  [LIB] version.py - 38 lines
windows/bridge_installation/venv/Lib/site-packages/pydantic/v1/
  [LIB] __init__.py - 1 lines
  [LIB] _hypothesis_plugin.py - 1 lines
  [LIB] annotated_types.py - 1 lines
  [LIB] class_validators.py - 1 lines
  [LIB] color.py - 1 lines
  [CONFIG] config.py - 1 lines
  [LIB] dataclasses.py - 1 lines
  [LIB] datetime_parse.py - 1 lines
  [LIB] decorator.py - 1 lines
  [LIB] env_settings.py - 1 lines
  [LIB] error_wrappers.py - 1 lines
  [LIB] errors.py - 1 lines
  [LIB] fields.py - 1 lines
  [LIB] generics.py - 1 lines
  [LIB] json.py - 1 lines
  [LIB] main.py - 1 lines
  [LIB] mypy.py - 1 lines
  [LIB] networks.py - 1 lines
  [LIB] parse.py - 1 lines
  [LIB] schema.py - 1 lines
  [LIB] tools.py - 1 lines
  [LIB] types.py - 1 lines
  [LIB] typing.py - 83 lines
  [LIB] utils.py - 1 lines
  [LIB] validators.py - 1 lines
  [LIB] version.py - 1 lines
windows/bridge_installation/venv/Lib/site-packages/requests/
  [LIB] __init__.py - 180 lines
  [LIB] __version__.py - 14 lines
  [LIB] _internal_utils.py - 50 lines
  [LIB] adapters.py - 538 lines
  [LIB] api.py - 157 lines
  [LIB] auth.py - 315 lines
  [LIB] certs.py - 17 lines
  [LIB] compat.py - 79 lines
  [LIB] cookies.py - 561 lines
  [LIB] exceptions.py - 141 lines
  [LIB] help.py - 134 lines
  [LIB] hooks.py - 33 lines
  [LIB] models.py - 1034 lines
  [LIB] packages.py - 28 lines
  [LIB] sessions.py - 833 lines (ports: 3128,4012)
  [LIB] status_codes.py - 128 lines
  [LIB] structures.py - 99 lines
  [LIB] utils.py - 1094 lines
windows/bridge_installation/venv/Lib/site-packages/sniffio/
  [LIB] __init__.py - 17 lines
  [LIB] _impl.py - 95 lines
  [LIB] _version.py - 3 lines
windows/bridge_installation/venv/Lib/site-packages/sniffio/_tests/
  [LIB] __init__.py - 0 lines
windows/bridge_installation/venv/Lib/site-packages/starlette/
  [LIB] __init__.py - 1 lines
  [LIB] _compat.py - 29 lines
  [LIB] _utils.py - 74 lines
  [LIB] applications.py - 261 lines
  [LIB] authentication.py - 153 lines
  [LIB] background.py - 43 lines
  [LIB] concurrency.py - 65 lines
  [CONFIG] config.py - 149 lines
  [LIB] convertors.py - 87 lines
  [LIB] datastructures.py - 708 lines
  [LIB] endpoints.py - 132 lines
  [LIB] exceptions.py - 54 lines
  [LIB] formparsers.py - 276 lines
  [LIB] requests.py - 318 lines
  [LIB] responses.py - 366 lines
  [LIB] routing.py - 862 lines
  [LIB] schemas.py - 146 lines
  [LIB] staticfiles.py - 246 lines
  [LIB] status.py - 199 lines
  [LIB] templating.py - 120 lines
  [TEST] testclient.py - 797 lines
  [LIB] types.py - 17 lines
  [LIB] websockets.py - 193 lines
windows/bridge_installation/venv/Lib/site-packages/starlette/middleware/
  [LIB] __init__.py - 17 lines
  [LIB] authentication.py - 52 lines
  [LIB] base.py - 134 lines
  [LIB] cors.py - 177 lines
  [LIB] errors.py - 256 lines
  [LIB] exceptions.py - 109 lines
  [LIB] gzip.py - 113 lines
  [LIB] httpsredirect.py - 19 lines
  [LIB] sessions.py - 86 lines
  [LIB] trustedhost.py - 60 lines
  [LIB] wsgi.py - 140 lines
windows/bridge_installation/venv/Lib/site-packages/urllib3/
  [LIB] __init__.py - 211 lines
  [LIB] _base_connection.py - 165 lines
  [LIB] _collections.py - 479 lines
  [LIB] _request_methods.py - 278 lines
  [LIB] _version.py - 21 lines
  [LIB] connection.py - 1093 lines
  [LIB] connectionpool.py - 1178 lines
  [LIB] exceptions.py - 335 lines (ports: 8080)
  [LIB] fields.py - 341 lines
  [LIB] filepost.py - 89 lines
  [LIB] poolmanager.py - 653 lines (ports: 3128)
  [LIB] response.py - 1307 lines
windows/bridge_installation/venv/Lib/site-packages/urllib3/contrib/
  [LIB] __init__.py - 0 lines
  [LIB] pyopenssl.py - 564 lines
  [LIB] socks.py - 228 lines
windows/bridge_installation/venv/Lib/site-packages/urllib3/contrib/emscripten/
  [LIB] __init__.py - 16 lines
  [LIB] connection.py - 255 lines
  [LIB] fetch.py - 728 lines
  [LIB] request.py - 22 lines
  [LIB] response.py - 277 lines
windows/bridge_installation/venv/Lib/site-packages/urllib3/http2/
  [LIB] __init__.py - 53 lines
  [LIB] connection.py - 356 lines
  [LIB] probe.py - 87 lines
windows/bridge_installation/venv/Lib/site-packages/urllib3/util/
  [LIB] __init__.py - 42 lines
  [LIB] connection.py - 137 lines
  [LIB] proxy.py - 43 lines
  [LIB] request.py - 266 lines
  [LIB] response.py - 101 lines
  [LIB] retry.py - 533 lines
  [LIB] ssl_.py - 524 lines
  [LIB] ssl_match_hostname.py - 159 lines
  [LIB] ssltransport.py - 271 lines
  [LIB] timeout.py - 275 lines
  [LIB] url.py - 469 lines
  [LIB] util.py - 42 lines
  [LIB] wait.py - 124 lines
windows/bridge_installation/venv/Lib/site-packages/uvicorn/
  [LIB] __init__.py - 5 lines
  [LIB] __main__.py - 4 lines
  [LIB] _subprocess.py - 76 lines
  [LIB] _types.py - 14 lines
  [CONFIG] config.py - 587 lines
  [LIB] importer.py - 38 lines
  [LIB] logging.py - 122 lines
  [LIB] main.py - 578 lines
  [SVC] server.py - 308 lines
  [LIB] workers.py - 105 lines
windows/bridge_installation/venv/Lib/site-packages/uvicorn/lifespan/
  [LIB] __init__.py - 0 lines
  [LIB] off.py - 12 lines
  [LIB] on.py - 137 lines
windows/bridge_installation/venv/Lib/site-packages/uvicorn/loops/
  [LIB] __init__.py - 0 lines
  [LIB] asyncio.py - 10 lines
  [LIB] auto.py - 11 lines
  [LIB] uvloop.py - 7 lines
windows/bridge_installation/venv/Lib/site-packages/uvicorn/middleware/
  [LIB] __init__.py - 0 lines
  [LIB] asgi2.py - 20 lines
  [LIB] message_logger.py - 89 lines
  [LIB] proxy_headers.py - 78 lines
  [LIB] wsgi.py - 190 lines
windows/bridge_installation/venv/Lib/site-packages/uvicorn/protocols/
  [LIB] __init__.py - 0 lines
  [LIB] utils.py - 55 lines
windows/bridge_installation/venv/Lib/site-packages/uvicorn/protocols/http/
  [LIB] __init__.py - 0 lines
  [LIB] auto.py - 14 lines
  [LIB] flow_control.py - 68 lines
  [LIB] h11_impl.py - 560 lines
  [LIB] httptools_impl.py - 594 lines
windows/bridge_installation/venv/Lib/site-packages/uvicorn/protocols/websockets/
  [LIB] __init__.py - 0 lines
  [LIB] auto.py - 19 lines
  [LIB] websockets_impl.py - 367 lines
  [LIB] wsproto_impl.py - 311 lines
windows/bridge_installation/venv/Lib/site-packages/uvicorn/supervisors/
  [LIB] __init__.py - 21 lines
  [LIB] basereload.py - 113 lines
  [LIB] multiprocess.py - 74 lines
  [LIB] statreload.py - 53 lines
  [LIB] watchfilesreload.py - 89 lines
  [LIB] watchgodreload.py - 158 lines
windows/bridge_installation/venv/Lib/site-packages/websockets/
  [LIB] __init__.py - 114 lines
  [LIB] __main__.py - 159 lines
  [LIB] auth.py - 4 lines
  [LIB] client.py - 358 lines
  [LIB] connection.py - 13 lines
  [LIB] datastructures.py - 200 lines
  [LIB] exceptions.py - 403 lines
  [LIB] frames.py - 449 lines
  [LIB] headers.py - 587 lines
  [LIB] http.py - 30 lines
  [LIB] http11.py - 364 lines
  [LIB] imports.py - 99 lines
  [LIB] protocol.py - 707 lines
  [SVC] server.py - 575 lines
  [LIB] streams.py - 151 lines
  [LIB] typing.py - 60 lines
  [LIB] uri.py - 108 lines
  [LIB] utils.py - 51 lines
  [LIB] version.py - 78 lines
windows/bridge_installation/venv/Lib/site-packages/websockets/extensions/
  [LIB] __init__.py - 4 lines
  [LIB] base.py - 133 lines
  [LIB] permessage_deflate.py - 660 lines
windows/bridge_installation/venv/Lib/site-packages/websockets/legacy/
  [LIB] __init__.py - 0 lines
  [LIB] async_timeout.py - 265 lines
  [LIB] auth.py - 184 lines
  [LIB] client.py - 713 lines
  [LIB] compatibility.py - 33 lines
  [LIB] framing.py - 176 lines
  [LIB] handshake.py - 165 lines
  [LIB] http.py - 201 lines
  [LIB] protocol.py - 1642 lines
  [SVC] server.py - 1196 lines
windows/bridge_installation/venv/Lib/site-packages/websockets/sync/
  [LIB] __init__.py - 0 lines
  [LIB] client.py - 328 lines
  [LIB] compatibility.py - 21 lines
  [LIB] connection.py - 757 lines
  [LIB] messages.py - 281 lines
  [SVC] server.py - 525 lines
  [LIB] utils.py - 46 lines
```

## Configuration Files

### .env
Variables defined: 
### config_drift_history.json
```yaml
- config_files:
    requirements.txt:
      content_hash: 3410944648151052321
      last_modified: '2025-07-22T10:47:10.638665'
      size: 893
  config_hash: 5000182dc7829bee4b583ac3680c67da
  environment_vars:
    HOME: /home/colindo
    PATH: /home/colindo/Sync/minh_v3/venv/bin:/home/colindo/.npm-global/bin:/home/colindo/.local/bin:/home/colindo/bin:/home/colindo/.npm-global/bin:/home/colindo/.cargo/bin:/home/colindo/.local/bin:/home/colindo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/usr/local/go/bin:/usr/local/go/bin:/usr/local/go/bin:/usr/local/go/bin:/home/colindo/.vscode/extensions/ms-python.debugpy-2025.10.0-linux-x64/bundled/scripts/noConfigScripts
    PYTHONPATH: NOT_SET
    USER: colindo
  system_info:
    architecture: 64bit
    platform: Linux-6.12.10-76061203-generic-x86_64-with-glibc2.35
    python_version: 3.10.12
  timestamp: '2025-07-24T11:35:49.734224'

```
### docker-compose.yml
```yaml
networks:
  default:
    name: minhos_network
services:
  grafana:
    container_name: minhos_grafana
    environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
    image: grafana/grafana:latest
    ports:
    - 3000:3000
    profiles:
    - monitoring
    restart: unless-stopped
    volumes:
    - grafana_data:/var/lib/grafana
    - ./monitoring/grafana:/etc/grafana/provisioning
  jaeger:
    container_name: minhos_jaeger
    environment:
    - COLLECTOR_OTLP_ENABLED=true
    image: jaegertracing/all-in-one:latest
    ports:
    - 16686:16686
    - 14268:14268
    profiles:
    - tracing
    restart: unless-stopped
  jupyter:
    container_name: minhos_jupyter
    environment:
    - JUPYTER_ENABLE_LAB=yes
    - JUPYTER_TOKEN=minhos
    image: jupyter/scipy-notebook:latest
    ports:
    - 8888:8888
    profiles:
    - analysis
    restart: unless-stopped
    volumes:
    - ./notebooks:/home/jovyan/work
    - ./data:/home/jovyan/data:ro
  minio:
    command: server /data --console-address ":9001"
    container_name: minhos_minio
    environment:
    - MINIO_ROOT_USER=minioadmin
    - MINIO_ROOT_PASSWORD=minioadmin123
    image: minio/minio:latest
    ports:
    - 9000:9000
    - 9001:9001
    profiles:
    - storage
    restart: unless-stopped
    volumes:
    - minio_data:/data
  postgres:
    container_name: minhos_postgres
    environment:
      POSTGRES_DB: minhos
      POSTGRES_INITDB_ARGS: --encoding=UTF-8 --lc-collate=C --lc-ctype=C
      POSTGRES_PASSWORD: minhos_dev_pass
      POSTGRES_USER: minhos
    healthcheck:
      interval: 10s
      retries: 5
      test:
      - CMD-SHELL
      - pg_isready -U minhos -d minhos
      timeout: 5s
    image: timescale/timescaledb:latest-pg14
    ports:
    - 5432:5432
    restart: unless-stopped
    volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
  prometheus:
    command:
    - --config.file=/etc/prometheus/prometheus.yml
    - --storage.tsdb.path=/prometheus
    - --web.console.libraries=/etc/prometheus/console_libraries
    - --web.console.templates=/etc/prometheus/consoles
    - --storage.tsdb.retention.time=30d
    - --web.enable-lifecycle
    container_name: minhos_prometheus
    image: prom/prometheus:latest
    ports:
    - 9090:9090
    profiles:
    - monitoring
    restart: unless-stopped
    volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  redis:
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    container_name: minhos_redis
    healthcheck:
      interval: 10s
      retries: 3
      test:
      - CMD
      - redis-cli
      - ping
      timeout: 3s
    image: redis:7-alpine
    ports:
    - 6379:6379
    restart: unless-stopped
    volumes:
    - redis_data:/data
version: '3.8'
volumes:
  grafana_data:
    driver: local
  minio_data:
    driver: local
  postgres_data:
    driver: local
  prometheus_data:
    driver: local
  redis_data:
    driver: local

```

## API Endpoints Discovered

- /api/Object
- /api/SMfuncs
- /api/ai
- /api/compute
- /api/config
- /api/datatypes
- /api/debug
- /api/file
- /api/file/info
- /api/file/list
- /api/file/read
- /api/file/read_binary
- /api/generate
- /api/health
- /api/index
- /api/java
- /api/latest-data
- /api/market
- /api/market_data
- /api/market_stream
- /api/notify
- /api/opengl
- /api/performance
- /api/positions
- /api/pydantic
- /api/risk
- /api/services
- /api/sfc-spec
- /api/stats
- /api/status
- /api/symbols
- /api/system
- /api/toplevel
- /api/trade
- /api/trade/execute
- /api/trade/status/{command_id}
- /api/trading
- /api/v1
- /files/
- /health
- /items/
- /items/{item_id}
- /login
- /send-notification/{email}
- /status
- /uploadfile/
- /users/me
- /users/me/items/

## Dependencies

### [WARNING] Missing Dependencies

- uvicorn[standard]
- python-multipart
- aiofiles
- pandas
- scikit-learn
- ta-lib
- yfinance
- python-decouple
- rich
- pytest
- pytest-asyncio
- pytest-cov
- black
- isort
- mypy
- ruff
- jupyter
- matplotlib
- seaborn
- plotly

### Required Dependencies

- [INSTALLED] fastapi==0.104.1
- [MISSING] uvicorn[standard]==0.24.0
- [INSTALLED] pydantic==2.5.0
- [MISSING] python-multipart==0.0.6
- [INSTALLED] aiohttp==3.9.0
- [MISSING] aiofiles==23.2.1
- [INSTALLED] websockets==11.0.2
- [INSTALLED] redis==5.0.1
- [INSTALLED] sqlalchemy==2.0.23
- [INSTALLED] alembic==1.12.1
- [INSTALLED] asyncpg==0.29.0
- [INSTALLED] aiosqlite==0.19.0
- [INSTALLED] numpy==1.24.3
- [MISSING] pandas==2.0.3
- [INSTALLED] scipy==1.11.4
- [MISSING] scikit-learn==1.3.2
- [INSTALLED] joblib==1.3.2
- [MISSING] ta-lib==0.4.26
- [MISSING] yfinance==0.2.22
- [INSTALLED] pyyaml==6.0.1
- [MISSING] python-decouple==3.8
- [INSTALLED] python-dateutil==2.8.2
- [INSTALLED] pytz==2023.3
- [INSTALLED] click==8.1.7
- [MISSING] rich==13.7.0
- [INSTALLED] prometheus-client==0.19.0
- [INSTALLED] psutil==5.9.6
- [MISSING] pytest==7.4.3
- [MISSING] pytest-asyncio==0.21.1
- [MISSING] pytest-cov==4.1.0
- [MISSING] black==23.11.0
- [MISSING] isort==5.12.0
- [MISSING] mypy==1.7.1
- [MISSING] ruff==0.1.6
- [MISSING] jupyter==1.0.0
- [MISSING] matplotlib==3.7.2
- [MISSING] seaborn==0.13.0
- [MISSING] plotly==5.17.0

## Port Configuration Validation

**Status: ✅ PASSED** - All port references are consistent

### Expected Port Configuration

| Service | Expected Port |
|---------|--------------|
| ai_brain_service | 9006 |
| live_integration | 9005 |
| minhos_dashboard | 8888 |
| multi_chart_collector | 9004 |
| risk_manager | 9009 |
| sierra_bridge | 8765 |
| sierra_client | 9003 |
| state_manager | 9008 |
| trading_engine | 9007 |

## Using This Report

1. **For AI Context**: Copy this entire report when asking for help
2. **For Debugging**: Check service health and recent errors
3. **For Development**: See file structure and dependencies
4. **For Verification**: Compare actual state vs expected state

To regenerate: `python system_truth.py`