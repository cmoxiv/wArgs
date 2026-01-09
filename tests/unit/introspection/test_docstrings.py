"""Unit tests for docstring parsing."""

from __future__ import annotations

from wArgs.introspection.docstrings import (
    DocstringFormat,
    DocstringInfo,
    detect_docstring_format,
    parse_docstring,
)


class TestDetectDocstringFormat:
    """Tests for docstring format detection."""

    def test_detect_google_args(self) -> None:
        """Test detection of Google-style with Args section."""
        docstring = """Summary.

        Args:
            param1: Description.
        """
        assert detect_docstring_format(docstring) == DocstringFormat.GOOGLE

    def test_detect_google_returns(self) -> None:
        """Test detection of Google-style with Returns section."""
        docstring = """Summary.

        Returns:
            The result.
        """
        assert detect_docstring_format(docstring) == DocstringFormat.GOOGLE

    def test_detect_google_raises(self) -> None:
        """Test detection of Google-style with Raises section."""
        docstring = """Summary.

        Raises:
            ValueError: When invalid.
        """
        assert detect_docstring_format(docstring) == DocstringFormat.GOOGLE

    def test_detect_numpy(self) -> None:
        """Test detection of NumPy-style docstring."""
        docstring = """Summary.

        Parameters
        ----------
        param1 : str
            Description.
        """
        assert detect_docstring_format(docstring) == DocstringFormat.NUMPY

    def test_detect_sphinx_param(self) -> None:
        """Test detection of Sphinx-style with :param."""
        docstring = """Summary.

        :param param1: Description.
        """
        assert detect_docstring_format(docstring) == DocstringFormat.SPHINX

    def test_detect_sphinx_type(self) -> None:
        """Test detection of Sphinx-style with :type."""
        docstring = """Summary.

        :type param1: str
        """
        assert detect_docstring_format(docstring) == DocstringFormat.SPHINX

    def test_detect_unknown(self) -> None:
        """Test detection of unknown format."""
        docstring = """Just a simple docstring without any special sections."""
        assert detect_docstring_format(docstring) == DocstringFormat.UNKNOWN

    def test_detect_empty(self) -> None:
        """Test detection with empty docstring."""
        assert detect_docstring_format("") == DocstringFormat.UNKNOWN
        assert detect_docstring_format(None) == DocstringFormat.UNKNOWN


class TestParseGoogleDocstring:
    """Tests for parsing Google-style docstrings."""

    def test_parse_summary(self) -> None:
        """Test extraction of summary."""
        docstring = """This is the summary.

        And this is more detail.
        """
        info = parse_docstring(docstring)
        assert info.summary == "This is the summary."

    def test_parse_args_single(self) -> None:
        """Test parsing single argument."""
        docstring = """Summary.

        Args:
            name: The name to use.
        """
        info = parse_docstring(docstring)
        assert "name" in info.params
        assert info.params["name"] == "The name to use."

    def test_parse_args_multiple(self) -> None:
        """Test parsing multiple arguments."""
        docstring = """Summary.

        Args:
            name: The name to use.
            count: How many times.
            verbose: Enable verbose output.
        """
        info = parse_docstring(docstring)
        assert len(info.params) == 3
        assert info.params["name"] == "The name to use."
        assert info.params["count"] == "How many times."
        assert info.params["verbose"] == "Enable verbose output."

    def test_parse_args_with_type(self) -> None:
        """Test parsing arguments with type annotations in docstring."""
        docstring = """Summary.

        Args:
            name (str): The name to use.
            count (int): How many times.
        """
        info = parse_docstring(docstring)
        assert info.params["name"] == "The name to use."
        assert info.params["count"] == "How many times."

    def test_parse_args_multiline(self) -> None:
        """Test parsing arguments with multiline descriptions."""
        docstring = """Summary.

        Args:
            name: The name to use. This description
                continues on the next line.
        """
        info = parse_docstring(docstring)
        assert "continues on the next line" in info.params["name"]

    def test_parse_returns(self) -> None:
        """Test parsing Returns section."""
        docstring = """Summary.

        Returns:
            The computed result.
        """
        info = parse_docstring(docstring)
        assert info.returns == "The computed result."

    def test_parse_raises(self) -> None:
        """Test parsing Raises section."""
        docstring = """Summary.

        Raises:
            ValueError: When the input is invalid.
            TypeError: When the type is wrong.
        """
        info = parse_docstring(docstring)
        assert "ValueError" in info.raises
        assert "When the input is invalid." in info.raises["ValueError"]

    def test_parse_full_docstring(self) -> None:
        """Test parsing complete Google docstring."""
        docstring = """Short summary of the function.

        Longer description that explains what the function does
        in more detail.

        Args:
            param1: Description of first parameter.
            param2: Description of second parameter.

        Returns:
            Description of return value.

        Raises:
            ValueError: If something is wrong.
        """
        info = parse_docstring(docstring)
        assert info.format == DocstringFormat.GOOGLE
        assert info.summary == "Short summary of the function."
        assert len(info.params) == 2
        assert info.returns is not None
        assert len(info.raises) == 1


class TestParseNumpyDocstring:
    """Tests for parsing NumPy-style docstrings."""

    def test_parse_summary(self) -> None:
        """Test extraction of summary."""
        docstring = """This is the summary.

        Parameters
        ----------
        name : str
            The name.
        """
        info = parse_docstring(docstring)
        assert info.summary == "This is the summary."
        assert info.format == DocstringFormat.NUMPY

    def test_parse_params(self) -> None:
        """Test parsing parameters section."""
        docstring = """Summary.

        Parameters
        ----------
        name : str
            The name to use.
        count : int
            How many times.
        """
        info = parse_docstring(docstring)
        assert "name" in info.params
        assert "count" in info.params
        assert "The name to use." in info.params["name"]

    def test_parse_params_multiline(self) -> None:
        """Test parsing parameters with multiline descriptions."""
        docstring = """Summary.

        Parameters
        ----------
        name : str
            The name to use. This is a longer
            description that spans multiple lines.
        """
        info = parse_docstring(docstring)
        assert "multiple lines" in info.params["name"]

    def test_parse_returns(self) -> None:
        """Test parsing Returns section."""
        docstring = """Summary.

        Parameters
        ----------
        x : int
            Input value.

        Returns
        -------
        int
            The computed result.
        """
        info = parse_docstring(docstring)
        assert info.returns is not None
        assert "computed result" in info.returns

    def test_parse_returns_single_line(self) -> None:
        """Test parsing Returns section with just type."""
        docstring = """Summary.

        Parameters
        ----------
        x : int
            Input value.

        Returns
        -------
        int
        """
        info = parse_docstring(docstring)
        assert info.returns is not None

    def test_parse_raises(self) -> None:
        """Test parsing Raises section in NumPy format."""
        docstring = """Summary.

        Parameters
        ----------
        x : int
            Input value.

        Raises
        ------
        ValueError
            If x is negative.
        """
        info = parse_docstring(docstring)
        assert "ValueError" in info.raises


class TestParseSphinxDocstring:
    """Tests for parsing Sphinx-style docstrings."""

    def test_parse_summary(self) -> None:
        """Test extraction of summary."""
        docstring = """This is the summary.

        :param name: The name.
        """
        info = parse_docstring(docstring)
        assert info.summary == "This is the summary."
        assert info.format == DocstringFormat.SPHINX

    def test_parse_param(self) -> None:
        """Test parsing :param directive."""
        docstring = """Summary.

        :param name: The name to use.
        :param count: How many times.
        """
        info = parse_docstring(docstring)
        assert info.params["name"] == "The name to use."
        assert info.params["count"] == "How many times."

    def test_parse_returns(self) -> None:
        """Test parsing :returns directive."""
        docstring = """Summary.

        :returns: The computed result.
        """
        info = parse_docstring(docstring)
        assert info.returns == "The computed result."

    def test_parse_return_singular(self) -> None:
        """Test parsing :return directive (singular)."""
        docstring = """Summary.

        :return: The computed result.
        """
        info = parse_docstring(docstring)
        assert info.returns == "The computed result."

    def test_parse_raises(self) -> None:
        """Test parsing :raises directive."""
        docstring = """Summary.

        :raises ValueError: When invalid.
        """
        info = parse_docstring(docstring)
        assert "ValueError" in info.raises


class TestParseUnknownFormat:
    """Tests for parsing unknown format docstrings."""

    def test_parse_plain_docstring(self) -> None:
        """Test parsing plain docstring."""
        docstring = """This is just a plain docstring.

        It has multiple lines but no special formatting.
        """
        info = parse_docstring(docstring)
        assert info.format == DocstringFormat.UNKNOWN
        assert info.summary == "This is just a plain docstring."
        assert info.description is not None

    def test_parse_empty_docstring(self) -> None:
        """Test parsing empty docstring."""
        info = parse_docstring("")
        assert info.format == DocstringFormat.UNKNOWN
        assert info.summary is None
        assert info.params == {}

    def test_parse_none_docstring(self) -> None:
        """Test parsing None docstring."""
        info = parse_docstring(None)
        assert info.format == DocstringFormat.UNKNOWN
        assert info.summary is None


class TestDocstringInfo:
    """Tests for DocstringInfo dataclass."""

    def test_default_values(self) -> None:
        """Test DocstringInfo has correct defaults."""
        info = DocstringInfo()
        assert info.summary is None
        assert info.description is None
        assert info.params == {}
        assert info.returns is None
        assert info.raises == {}
        assert info.format == DocstringFormat.UNKNOWN

    def test_params_is_mutable(self) -> None:
        """Test that each instance has its own params dict."""
        info1 = DocstringInfo()
        info2 = DocstringInfo()

        info1.params["name"] = "description"
        assert "name" not in info2.params
