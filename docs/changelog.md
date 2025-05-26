# Changelog

All notable changes to the Baten Chess Engine project are documented in this file.

## \[v0.2] - 2025-05-26

* Cleaned up DSL validator (`validator_dsl.py`) to pure movement logic
* Introduced `rules.py` for full rule engine: turn management, en-passant, castling, pins
* Added REST API reference (`app_api.md`)
* Added Board API reference (`board_api.md`)
* Created initial documentation: `contributing.md`, `faq.md`

## \[v0.1] - 2025-05-25

* Initial release
* Python prototype with combined validator and rules
* Flask UI with drag-and-drop chessboard
* Basic movement validation for all pieces
* Introduced DSL generation infrastructure

> For older changes, check Git tags in the repository.
