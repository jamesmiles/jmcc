#!/usr/bin/env python3
"""
JMCC Test Runner

Discovers and runs all tests, validates against reference compilers,
and reports the reward signal (pass rate).
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from harness.run import (
    ensure_docker_image,
    parse_test_metadata,
    run_test,
)

APPLE_PHASE1_TESTS = (
    "positive/phase1/001_return_zero.c",
    "positive/phase1/002_return_literal.c",
    "positive/phase1/003_addition.c",
    "positive/phase1/004_subtraction.c",
    "positive/phase1/006_division.c",
    "positive/phase1/007_modulo.c",
    "positive/phase1/008_negation.c",
    "positive/phase1/009_bitwise_and.c",
    "positive/phase1/010_bitwise_or.c",
    "positive/phase1/011_local_var.c",
    "positive/phase1/012_multiple_vars.c",
    "positive/phase1/013_if_true.c",
    "positive/phase1/014_if_false.c",
    "positive/phase1/015_if_else.c",
    "positive/phase1/016_comparison_eq.c",
    "positive/phase1/017_comparison_ne.c",
    "positive/phase1/018_comparison_lt.c",
    "positive/phase1/019_while_loop.c",
    "positive/phase1/020_for_loop.c",
    "positive/phase1/021_function_call.c",
    "positive/phase1/022_recursive_factorial.c",
    "positive/phase1/023_logical_and.c",
    "positive/phase1/024_logical_or.c",
    "positive/phase1/025_logical_not.c",
    "positive/phase1/026_nested_if.c",
    "positive/phase1/027_complex_expr.c",
    "positive/phase1/028_parenthesized_expr.c",
    "positive/phase1/030_bitwise_xor.c",
    "positive/phase1/031_shift_left.c",
    "positive/phase1/032_shift_right.c",
    "positive/phase1/034_var_assignment.c",
    "positive/phase1/029_do_while.c",
    "positive/phase1/033_global_var.c",
    "positive/phase2/001_compound_assign.c",
    "positive/phase2/002_prefix_inc.c",
    "positive/phase2/003_postfix_inc.c",
    "positive/phase2/004_ternary.c",
    "positive/phase2/005_switch.c",
    "positive/phase2/006_switch_fallthrough.c",
    "positive/phase2/007_break_loop.c",
    "positive/phase2/008_continue_loop.c",
    "positive/phase2/009_pointer_basic.c",
    "positive/phase2/010_pointer_write.c",
    "positive/phase2/011_array_basic.c",
    "positive/phase2/012_array_sum.c",
    "positive/phase2/013_sizeof_int.c",
    "positive/phase2/014_sizeof_char.c",
    "positive/phase2/015_sizeof_pointer.c",
    "positive/phase2/016_goto.c",
    "positive/phase2/017_char_type.c",
    "positive/phase2/018_multiple_functions.c",
    "positive/phase2/019_nested_loops.c",
    "positive/phase2/020_pointer_arithmetic.c",
    "positive/phase2/021_for_with_decl.c",
    "positive/phase2/022_hex_literal.c",
    "positive/phase2/023_octal_literal.c",
    "positive/phase2/024_char_escape.c",
    "positive/phase2/025_comparison_chain.c",
    "positive/phase3/003_enum_basic.c",
    "positive/phase3/004_enum_explicit.c",
    "positive/phase3/005_typedef_basic.c",
    "positive/phase3/001_struct_basic.c",
    "positive/phase3/002_struct_pointer.c",
    "positive/phase3/006_string_literal.c",
    "positive/phase3/007_long_type.c",
    "positive/phase3/008_unsigned_type.c",
    "positive/phase3/009_forward_decl.c",
    "positive/phase3/010_global_init.c",
    "positive/phase3/011_struct_pass.c",
    "positive/phase3/012_array_of_structs.c",
    "positive/phase3/013_printf_hello.c",
    "positive/phase3/014_printf_int.c",
    "positive/phase3/015_fibonacci.c",
    "positive/phase3/016_linked_list.c",
    "positive/phase3/017_void_func.c",
    "positive/phase3/018_multiple_returns.c",
    "positive/phase3/019_nested_struct.c",
    "positive/phase3/020_global_array.c",
    "positive/phase3/021_define_const.c",
    "positive/phase3/022_define_expr.c",
    "positive/phase3/023_ifdef.c",
    "positive/phase3/024_ifndef.c",
    "positive/phase3/025_func_macro.c",
    "positive/phase3/026_include_stdbool.c",
    "positive/phase3/027_include_limits.c",
    "positive/phase3/028_printf_string_var.c",
    "positive/phase3/029_printf_multiple.c",
    "positive/phase3/030_bubble_sort.c",
    "positive/phase3/031_binary_search.c",
    "positive/phase3/032_string_length.c",
    "positive/phase3/033_gcd.c",
    "positive/phase3/035_typedef_struct.c",
    "positive/phase3/036_enum_switch.c",
    "positive/phase3/037_string_compare.c",
    "positive/phase3/039_array_pointer_decay.c",
    "positive/phase3/040_recursive_power.c",
    "positive/phase3/042_nested_loops_break.c",
    "positive/phase3/034_tower_of_hanoi.c",
    "positive/phase3/038_printf_format.c",
    "positive/phase3/041_struct_return_ptr.c",
    "positive/phase3/043_pointer_to_pointer.c",
    "positive/phase3/044_global_string_init.c",
    "positive/phase3/045_define_guard.c",
    "positive/phase3/046_variadic_printf.c",
    "positive/phase3/047_bitfield_ops.c",
    "positive/phase3/048_array_as_param.c",
    "positive/phase3/049_multiline_printf.c",
    "positive/phase3/050_conditional_assign.c",
    "positive/phase4/001_static_local.c",
    "positive/phase4/002_comma_operator.c",
    "positive/phase4/003_cast_int_to_char.c",
    "positive/phase4/004_sizeof_types.c",
    "positive/phase4/005_sizeof_expr.c",
    "positive/phase4/006_func_pointer_call.c",
    "positive/phase4/007_struct_init_local.c",
    "positive/phase4/008_multidim_array.c",
    "positive/phase4/009_global_2d_array.c",
    "positive/phase4/010_printf_double_then_int.c",
    "positive/phase4/011_printf_many_doubles_then_ints.c",
    "positive/phase5/011_quoted_include.c",
    "positive/phase5/012_nested_include.c",
    "positive/phase5/013_include_guard.c",
    "positive/phase5/001_longlong_multiply.c",
    "positive/phase5/002_longlong_shift.c",
    "positive/phase5/003_fixedpoint_doom.c",
    "positive/phase5/004_longlong_cast_signextend.c",
    "positive/phase5/005_longlong_literal.c",
    "positive/phase5/006_extern_variable.c",
    "positive/phase5/007_extern_function.c",
    "positive/phase5/008_static_function.c",
    "positive/phase5/009_static_global.c",
    "positive/phase5/010_multifile_struct.c",
    "positive/phase5/014_pragma_ignore.c",
    "positive/phase5/015_actionf_union.c",
    "positive/phase5/016_func_pointer_array.c",
    "positive/phase5/017_func_pointer_cast.c",
    "positive/phase5/018_large_switch.c",
    "positive/phase5/019_switch_enum.c",
    "positive/phase5/020_bit_manipulation.c",
    "positive/phase5/021_hex_shift.c",
    "positive/phase5/022_struct_array_member.c",
    "positive/phase5/023_thinker_linked_list.c",
    "positive/phase5/024_void_ptr_cast.c",
    "positive/phase5/025_string_table.c",
    "positive/phase5/026_register_keyword.c",
    "positive/phase5/027_alloca_vla.c",
    "positive/phase5/028_macro_line_continuation.c",
    "positive/phase5/029_enum_const_expr.c",
    "positive/phase5/030_system_define_substitute.c",
    "positive/phase5/031_short_array_struct_member.c",
    "positive/phase5/032_macro_comment_strip.c",
    "positive/phase5/033_values_h_minint.c",
    "positive/phase5/034_float_literal_no_leading_zero.c",
    "positive/phase5/035_lvalue_after_switch.c",
    "positive/phase5/036_system_header_constants.c",
    "positive/phase5/037_system_struct_stat.c",
    "positive/phase5/038_system_timeval.c",
    "positive/phase5/039_angle_bracket_include.c",
    "positive/phase5/041_include_unistd.c",
    "positive/phase5/042_include_fcntl.c",
    "positive/phase5/043_include_sys_stat.c",
    "positive/phase5/044_include_signal.c",
    "positive/phase5/045_include_sys_time.c",
    "positive/phase5/046_include_netinet_in.c",
    "positive/phase5/049_include_sys_socket.c",
    "positive/phase5/050_signal_sa_restart.c",
    "positive/phase5/052_socket_inaddr.c",
    "positive/phase5/053_itimerval.c",
    "positive/phase5/054_include_errno.c",
    "positive/phase5/055_include_netdb.c",
    "positive/phase5/056_include_sys_ioctl.c",
    "positive/phase5/058_cmdline_define.c",
    "positive/phase5/068_macro_multiline_args.c",
    "positive/phase1/005_multiplication.c",
    "positive/phase1/035_bitwise_not.c",
    "positive/phase5/062_include_sys_ipc_shm.c",
    "positive/phase5/069_comment_unmatched_paren.c",
    "positive/phase5/070_char_literal_paren.c",
    "positive/phase5/071_multiline_call_inline_comment.c",
    "positive/phase5/074_shm_perm.c",
    "positive/phase5/077_glibc_socklen_t.c",
    "positive/phase5/079_extern_func_pointer.c",
    "positive/phase5/080_alloca_builtin.c",
    "positive/phase5/081_struct_init_cast_ptr.c",
    "positive/phase5/082_struct_init_array_addr.c",
    "positive/phase5/083_char_ptr_array_iterate.c",
    "positive/phase5/084_struct_ptr_index_stride.c",
    "positive/phase5/085_double_ptr_struct_stride.c",
    "positive/phase5/086_global_char_ptr_string_init.c",
    "positive/phase5/087_short_member_write_clobber.c",
    "positive/phase5/088_global_ptr_array_element_init.c",
    "positive/phase5/089_compound_assign_short_clobber.c",
    "positive/phase5/090_incr_short_member_clobber.c",
    "positive/phase5/091_compound_assign_char_clobber.c",
    "positive/phase5/092_cast_sign_extension.c",
    "positive/phase5/093_compound_assign_long_truncate.c",
    "positive/phase5/094_incr_short_overflow_clobber.c",
    "positive/phase5/095_2d_struct_array_stride.c",
    "positive/phase5/097_2d_pointer_array_stride.c",
    "positive/phase5/099_2d_ptr_array_global_size.c",
    "positive/phase5/100_2d_array_init_size.c",
    "positive/phase5/101_array_size_const_expr.c",
    "positive/phase5/102_byte_member_unsigned_compare.c",
    "positive/phase5/103_truecolor_palette_convert.c",
    "positive/phase5/104_uchar_ptr_deref_unsigned.c",
    "positive/phase5/105_2d_uchar_array_unsigned.c",
    "positive/phase5/106_unsigned_char_all_access.c",
    "positive/phase5/107_unsigned_short_all_access.c",
    "positive/phase5/108_unsigned_division_modulo.c",
    "positive/phase5/109_unsigned_right_shift.c",
    "positive/phase5/110_unsigned_comparison.c",
    "positive/phase5/111_void_ptr_ptr_write.c",
    "positive/phase5/112_struct_sizeof_with_pointers.c",
    "positive/phase5/113_int_to_ptr_cast_store.c",
    "positive/phase5/114_pointer_truthiness_64bit.c",
    "positive/phase5/115_pointer_comparison_64bit.c",
    "positive/phase5/116_long_comparison_64bit.c",
    "positive/phase5/117_pointer_subtraction_large.c",
    "positive/phase5/118_unsigned_cast_comparison.c",
    "positive/phase5/119_unsigned_cast_operations.c",
    "positive/phase5/120_64bit_basics.c",
    "positive/phase5/121_function_pointer_64bit.c",
    "positive/phase5/122_pointer_int_cast_roundtrip.c",
    "positive/phase5/123_ptr_negative_offset.c",
    "positive/phase5/124_funcptr_double_indirect.c",
    "positive/phase5/125_charpp_double_index.c",
    "positive/phase5/126_struct_init_mixed_long_int.c",
    "positive/phase5/127_struct_array_union_init.c",
    "positive/phase5/128_charpp_int_cast_deref.c",
    "positive/phase5/129_struct_array_member_index.c",
    "positive/phase5/130_ptr_struct_member_array.c",
    "positive/phase5/131_ptr_array_null_terminator.c",
    "positive/phase5/132_global_ptr_postinc_deref.c",
    "positive/phase5/133_ptr_arrow_array_member.c",
    "positive/phase5/134_chained_arrow_access.c",
    "positive/phase5/135_typedef_unsigned_propagation.c",
    "positive/phase5/136_typedef_unsigned_shift.c",
    "positive/phase5/137_2d_array_partial_init.c",
    "positive/phase5/138_2d_member_array_decay.c",
    "positive/phase5/139_struct_array_member_decay.c",
    "positive/phase5/140_ptr_array_member_chain.c",
    "positive/phase5/141_double_to_int_negative.c",
    "positive/phase5/142_shortpp_double_index.c",
    "positive/phase5/143_ptr_plus_constant_stride.c",
    "positive/phase5/144_struct_assign_copy.c",
    "positive/phase5/145_struct_copy_variants.c",
    "positive/phase5/147_ptr_member_array_assign.c",
    "positive/phase5/148_ptr_assign_not_struct_copy.c",
    "positive/phase5/149_struct_array_elem_copy.c",
    "positive/phase5/150_ptr_member_index_submember.c",
    "positive/phase5/151_func_call_7plus_args.c",
    "positive/phase5/152_2d_array_row_init.c",
    "positive/phase5/153_array_member_define_plus_one.c",
    "positive/phase5/154_compound_shift_unsigned.c",
    "positive/phase5/155_compound_assign_unsigned_ops.c",
    "positive/phase5/157_variadic_va_list_abi.c",
    "positive/phase5/158_variadic_va_arg_direct.c",
    "positive/phase5/159_variadic_va_copy.c",
    "positive/phase5/160_2d_char_array_string_init.c",
    "positive/phase5/161_2d_array_init_variants.c",
    "positive/phase5/162_switch_negative_case.c",
    "positive/phase5/163_static_ptr_array_addr_init.c",
    "positive/phase5/164_array_sizeof_then_pass.c",
    "positive/phase5/165_typedef_attribute.c",
    "positive/phase5/166_restrict_qualifier.c",
    "positive/phase5/167_extension_keyword.c",
    "positive/phase5/168_static_assert.c",
    "positive/phase5/169_atomic_qualifier.c",
    "positive/phase5/170_attribute_before_decl.c",
    "positive/phase5/171_include_path_flag.c",
    "positive/phase5/172_asm_statement.c",
    "positive/phase5/173_variadic_macros.c",
    "positive/phase5/174_for_loop_declaration.c",
    "positive/phase5/175_stdbool.c",
    "positive/phase5/176_stdbool_defined_macro.c",
    "positive/phase5/177_func_ptr_array_decl.c",
    "positive/phase5/178_pointer_to_array_decl.c",
    "positive/phase5/179_paren_func_name_decl.c",
    "positive/phase5/180_struct_return_assign.c",
    "positive/phase5/181_cast_pointer_to_array.c",
    "positive/phase5/182_func_ptr_ptr_param.c",
    "positive/phase5/183_self_referential_macro.c",
    "positive/phase5/184_comma_decl_with_init.c",
    "positive/phase5/185_sizeof_anon_struct_element.c",
    "positive/phase5/186_typedef_array_param.c",
    "positive/phase5/187_nested_struct_array_init.c",
    "positive/phase5/188_asm_byteswap_function.c",
    "positive/phase5/189_has_builtin_macro.c",
    "positive/phase5/192_builtin_constant_p.c",
    "positive/phase5/193_compound_literal.c",
    "positive/phase5/195_gnuc_macro.c",
    "positive/phase5/196_ifdef_has_builtin.c",
    "positive/phase5/197_has_builtin_through_macro.c",
    "positive/phase5/198_packed_struct.c",
    "positive/phase5/199_func_returning_func_ptr.c",
    "positive/phase5/200_macro_arg_recursion.c",
    "positive/phase5/201_asm_label_alias.c",
    "positive/phase5/202_cast_to_func_ptr.c",
    "positive/phase5/203_cast_func_ptr_ptr_return.c",
    "positive/phase5/204_ptr_ptr_func_member.c",
    "positive/phase5/205_fcntl_constants.c",
    "positive/phase5/206_struct_flock.c",
    "positive/phase5/207_unistd_sysconf.c",
    "positive/phase5/208_stdio_constants.c",
    "positive/phase5/209_builtin_offsetof.c",
    "positive/phase5/210_cond_expr_struct.c",
    "positive/phase5/211_sys_stat_macros.c",
    "positive/phase5/212_va_list_chain.c",
    "positive/phase5/213_bitfield_writes.c",
    "positive/phase5/214_struct_ptr_array_decay.c",
    "positive/phase5/215_va_arg_double.c",
    "positive/phase5/216_u8_struct_member_deref.c",
    "positive/phase5/217_parenthesized_declarator.c",
    "positive/phase5/218_multi_declarator_pointer.c",
    "positive/phase5/219_static_array_of_pointers_init.c",
    "positive/phase5/220_array_typedef_indexing.c",
    "positive/phase5/221_vla_2d_stride.c",
    "positive/phase5/222_stdio_fclose_decl.c",
    "positive/phase5/223_generic_lvalue.c",
    "positive/phase5/226_string_literal_dedup.c",
    "positive/phase5/227_long_double_basic.c",
    "positive/phase5/229_float_bool_condition.c",
    "positive/phase5/233_static_ptr_array_member_addr.c",
    "positive/phase5/234_fnptr_returning_fnptr_cast.c",
    "positive/phase5/235_extern_redecl_after_defn.c",
    "positive/phase5/236_int128_basic.c",
    "positive/phase5/237_int128_arith.c",
    "positive/phase5/238_int128_mul_div.c",
    "positive/phase5/239_int128_fn_args.c",
    "positive/phase5/240_int128_shift_print.c",
    "positive/phase5/241_fnptr_double_deref_ptr_return.c",
    "positive/phase5/244_getpagesize.c",
    "positive/phase5/245_readlink_fchown_static_init.c",
    "positive/phase5/246_ternary_ptr_cltq_corruption.c",
    "positive/phase5/247_int32_to_int64_sign_extend.c",
    "positive/phase5/248_long_double_arithmetic.c",
    "positive/phase5/249_i64_signed_gt_int64min.c",
    "positive/phase5/250_signed_cmp_with_uint_subexpr.c",
    "positive/phase5/251_struct_array_sizeof_dimension.c",
    "positive/phase5/252_struct_inline_fnptr_void_ptr_ret.c",
    "positive/phase5/253_builtin_add_overflow.c",
    "positive/phase5/254_extern_decl_in_function_body.c",
    "positive/phase5/255_u64_to_double_implicit_cast.c",
    "positive/phase5/256_u64_to_double_ptr_assign.c",
    "positive/phase5/257_signed_char_to_i64_sign_extend.c",
    "positive/phase5/258_u64_to_double_highbit.c",
    "positive/phase5/260_double_to_u64_highbit.c",
    "positive/phase5/261_log10_log2_return_type.c",
    "positive/phase5/262_i64_to_double_conversion.c",
    "positive/phase5/263_int_to_i64_return_sign_extend.c",
    "positive/phase5/264_vararg_double_int_overflow.c",
    "positive/phase5/265_octal_escape_multidigit.c",
    "positive/phase5/266_sizeof_ptr_member_array_dim.c",
    "positive/phase5/267_asinh_acosh_atanh_return_type.c",
    "positive/phase5/268_math_funcptr_in_struct.c",
    "positive/phase5/269_nearbyint_rint_return_type.c",
    "positive/phase5/270_c99_math_missing_stubs.c",
    "positive/phase5/271_fma_fmax_fmin_return_type.c",
    "positive/phase5/273_builtin_va_list.c",
    "positive/phase5/274_struct_member_attribute.c",
    "positive/phase5/276_thread_local_storage.c",
    "positive/phase5/277_float_h_constants.c",
    "positive/phase5/278_sig_atomic_t.c",
    "positive/phase5/279_func_type_typedef.c",
    "positive/phase5/280_var_shadows_typedef.c",
    "positive/phase5/281_bitfield_comma_decl.c",
    "positive/phase5/282_fp_classification_macros.c",
    "positive/phase5/283_memory_order_enum.c",
    "positive/phase5/284_macro_3level_string_escape.c",
    "positive/phase5/285_typedef_shadow_arrow_in_parens.c",
    "positive/phase5/286_float_h_dbl_max.c",
    "positive/phase5/287_label_address_extension.c",
    "positive/phase5/288_comma_expr_member_access.c",
    "positive/phase5/289_winsize_struct.c",
    "positive/phase5/290_paren_func_type_typedef.c",
    "positive/phase5/291_const_func_ptr_member.c",
    "positive/phase5/292_double_paren_typedef_shadow.c",
    "positive/phase5/293_socket_options_constants.c",
    "positive/phase5/295_attribute_on_parameter.c",
    "positive/phase5/296_atomic_typedef_types.c",
    "positive/phase5/297_sizeof_array_constant_expr.c",
    "positive/phase5/298_gnuc_va_list.c",
    "positive/phase5/299_signal_stack_t.c",
    "positive/phase5/300_sys_stat_posix_typedefs.c",
    "positive/phase5/301_func_type_param.c",
    "positive/phase5/302_deeply_nested_casts.c",
    "positive/phase5/303_netdb_addrinfo.c",
    "positive/phase5/304_attribute_on_declarator.c",
    "positive/phase5/305_version_macro.c",
    "positive/phase5/306_func_predefined.c",
    "positive/phase5/307_ssize_max.c",
    "positive/phase5/308_signal_constants.c",
    "positive/phase5/309_ipv6_socket_structs.c",
    "positive/phase5/310_attribute_after_declarator.c",
    "positive/phase5/311_typedef_scope_restore.c",
    "positive/phase5/312_sockaddr_storage.c",
    "positive/phase5/313_iov_max.c",
    "positive/phase5/314_alignof.c",
    "positive/phase5/315_siginfo_t.c",
    "positive/phase5/316_af_local.c",
    "positive/phase5/317_builtin_va_list_typedef_arm64.c",
    "positive/phase5/318_nullable_nonnull_fnptr_arm64.c",
    "positive/phase5/319_block_ptr_syntax_arm64.c",
    "positive/phase5/320_nullable_in_struct_fields_arm64.c",
    "positive/phase5/321_typedef_opaque_struct_member_arm64.c",
    "positive/phase5/322_inttypes_uint_typedefs_arm64.c",
    "negative/semantic_errors/001_undeclared_var.c",
    "negative/semantic_errors/002_break_outside_loop.c",
    "negative/semantic_errors/003_continue_outside_loop.c",
    "negative/semantic_errors/004_duplicate_label.c",
    "negative/syntax_errors/001_missing_semicolon.c",
    "negative/syntax_errors/002_missing_brace.c",
    "negative/syntax_errors/003_missing_paren.c",
    "negative/syntax_errors/004_invalid_token.c",
    "negative/syntax_errors/005_double_semicolon_decl.c",
    "negative/syntax_errors/006_unclosed_comment.c",
    "negative/syntax_errors/007_empty_function.c",
    "negative/type_errors/001_void_arithmetic.c",
)

NAMED_SUITES = {
    "apple-phase1": APPLE_PHASE1_TESTS,
}


def discover_tests(test_dir, phase=None, filter_pattern=None, negative_only=False,
                   positive_only=False, suite=None):
    """Discover test files matching criteria."""
    tests = []

    if suite is not None:
        for rel_path in NAMED_SUITES[suite]:
            test_file = Path(test_dir, rel_path)
            metadata = parse_test_metadata(test_file)
            if phase is not None and metadata["phase"] != phase:
                continue
            if filter_pattern and filter_pattern not in str(test_file):
                continue
            tests.append(test_file)
        return tests

    if not negative_only:
        for phase_dir in sorted(Path(test_dir, "positive").glob("phase*")):
            for test_file in sorted(phase_dir.glob("*.c")):
                if test_file.name.endswith("_arm64.c"):
                    continue  # arm64-only tests; excluded from generic discovery
                metadata = parse_test_metadata(test_file)
                if not metadata["name"]:
                    continue  # Skip helper files (no // TEST: header)
                if phase is not None and metadata["phase"] != phase:
                    continue
                if filter_pattern and filter_pattern not in str(test_file):
                    continue
                tests.append(test_file)

    if not positive_only:
        for category_dir in sorted(Path(test_dir, "negative").iterdir()):
            if not category_dir.is_dir():
                continue
            for test_file in sorted(category_dir.glob("*.c")):
                metadata = parse_test_metadata(test_file)
                if phase is not None and metadata["phase"] != phase:
                    continue
                if filter_pattern and filter_pattern not in str(test_file):
                    continue
                tests.append(test_file)

    # External tests
    if not negative_only:
        external_dir = Path(test_dir, "external")
        if external_dir.exists():
            for test_file in sorted(external_dir.glob("**/*.c")):
                metadata = parse_test_metadata(test_file)
                if phase is not None and metadata["phase"] != phase:
                    continue
                if filter_pattern and filter_pattern not in str(test_file):
                    continue
                tests.append(test_file)

    return tests


def run_all_tests(tests, compiler="jmcc", validate_references=False, target=None):
    """Run all tests and return results."""
    results = []

    for test_file in tests:
        metadata = parse_test_metadata(test_file)
        test_name = metadata["name"] or test_file.stem

        # Optionally validate against reference compilers first
        if validate_references and not metadata["expect_compile_fail"]:
            for ref in ("gcc", "clang"):
                ref_result = run_test(test_file, compiler=ref)
                if not ref_result["passed"]:
                    print(f"  WARNING: {test_name} fails with {ref}: {ref_result['details']}")

        # Run with target compiler
        result = run_test(test_file, compiler=compiler, target=target)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  [{status}] {test_name}: {result['details']}")
        results.append(result)

    return results


def print_score(results):
    """Print the reward signal."""
    # Group by category
    positive = [r for r in results if not r["metadata"]["expect_compile_fail"]]
    negative = [r for r in results if r["metadata"]["expect_compile_fail"]]

    # Group positive by phase
    phases = {}
    for r in positive:
        p = r["metadata"]["phase"]
        if p not in phases:
            phases[p] = {"pass": 0, "total": 0}
        phases[p]["total"] += 1
        if r["passed"]:
            phases[p]["pass"] += 1

    neg_pass = sum(1 for r in negative if r["passed"])
    neg_total = len(negative)

    total_pass = sum(1 for r in results if r["passed"])
    total_total = len(results)

    print("\n=== JMCC Test Results ===")
    for p in sorted(phases.keys()):
        pct = (phases[p]["pass"] / phases[p]["total"] * 100) if phases[p]["total"] else 0
        print(f"Phase {p}: {phases[p]['pass']:>3}/{phases[p]['total']:<3} ({pct:>5.1f}%)")

    if neg_total:
        pct = (neg_pass / neg_total * 100) if neg_total else 0
        print(f"Negative: {neg_pass:>3}/{neg_total:<3} ({pct:>5.1f}%)")

    print("─" * 28)
    pct = (total_pass / total_total * 100) if total_total else 0
    print(f"TOTAL:    {total_pass:>3}/{total_total:<3} ({pct:>5.1f}%)")
    print()

    return total_pass, total_total


def main():
    parser = argparse.ArgumentParser(description="JMCC Test Runner")
    parser.add_argument("--phase", type=int, help="Run only tests for given phase")
    parser.add_argument("--filter", type=str, help="Filter tests by name pattern")
    parser.add_argument("--compiler", default="jmcc", choices=["jmcc", "gcc", "clang"],
                        help="Compiler to test")
    parser.add_argument("--validate", action="store_true",
                        help="Also validate tests against reference compilers")
    parser.add_argument("--score", action="store_true",
                        help="Show only the score summary")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    parser.add_argument("--negative-only", action="store_true",
                        help="Run only negative tests")
    parser.add_argument("--positive-only", action="store_true",
                        help="Run only positive tests")
    parser.add_argument("--native", action="store_true",
                        help="Run without Docker (faster, uses host as/gcc)")
    parser.add_argument("--target", default=None,
                        help="JMCC compilation target (for jmcc compiler runs)")
    parser.add_argument("--suite", choices=sorted(NAMED_SUITES.keys()),
                        help="Run a named curated test suite")
    args = parser.parse_args()

    if args.native:
        os.environ["JMCC_NATIVE"] = "1"

    test_dir = PROJECT_DIR / "tests"

    # Discover tests
    tests = discover_tests(
        test_dir,
        phase=args.phase,
        filter_pattern=args.filter,
        negative_only=args.negative_only,
        positive_only=args.positive_only,
        suite=args.suite,
    )

    if not tests:
        print("No tests found.")
        sys.exit(0)

    print(f"Found {len(tests)} tests")

    # Ensure Docker image exists
    ensure_docker_image()

    # Run tests
    print(f"\nRunning tests with {args.compiler}...")
    results = run_all_tests(
        tests,
        compiler=args.compiler,
        validate_references=args.validate,
        target=args.target,
    )

    # Output
    if args.json:
        # Strip non-serializable bits
        for r in results:
            r["source"] = str(r["source"])
        print(json.dumps(results, indent=2))
    else:
        passed, total = print_score(results)
        sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
