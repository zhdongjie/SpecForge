package org.eu.originalkeen.core.utils;

import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.exception.business.FieldValidationException;
import org.eu.originalkeen.system.dictionary.data.service.DictionaryDataService;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * 翻译工具类
 * 提供多语言翻译相关的通用方法，如校验、过滤等
 */
@Slf4j
public class TranslationUtils {

    private static final DictionaryDataService dictionaryDataService = SpringUtils.getBean(DictionaryDataService.class);

    /**
     * 校验翻译数据
     * 校验翻译数据是否满足要求，包括校验重复语言、缺失语言等
     *
     * @param translations        翻译数据列表
     * @param getLanguageCodeFunc 获取语言代码的函数
     * @param <T>                 翻译数据类型
     * @throws FieldValidationException 当校验失败时抛出
     */
    public static <T> void validateTranslations(
            List<T> translations,
            Function<T, String> getLanguageCodeFunc
    ) {
        String validateField = "translations";
        // 获取所有已提交的语言代码
        List<String> submittedLangCodes = getSubmittedLanguageCodes(translations, getLanguageCodeFunc);

        // 校验是否有重复的语言代码
        Set<String> duplicateLangCodes = findDuplicates(submittedLangCodes);
        if (CollectionUtils.isNotEmpty(duplicateLangCodes)) {
            String duplicateCodes = String.join(", ", duplicateLangCodes);
            log.warn("Duplicate languages found: {}", duplicateCodes);
            throw new FieldValidationException(validateField, "form.common.duplicateLanguages", duplicateCodes);
        }

        // 获取所有系统支持的语言代码
        Set<String> supportedLangCodes = dictionaryDataService.selectAvailableValues(SystemConstant.DICTIONARY_CODE_LANGUAGE_CODE);

        // 校验语言代码是否有效
        Set<String> invalidLanguages = invalidLanguages(submittedLangCodes, supportedLangCodes);
        if (CollectionUtils.isNotEmpty(invalidLanguages)) {
            String invalidCodes = String.join(", ", invalidLanguages);
            String allowedCodes = String.join(", ", supportedLangCodes);
            log.warn("Invalid languages: {}", invalidCodes);
            throw new FieldValidationException(validateField, "form.common.invalidLanguages", invalidLanguages, allowedCodes);
        }

        // 校验是否所有支持的语言代码都已提交
        Set<String> missingLangCodes = findMissingLanguages(submittedLangCodes, supportedLangCodes);
        if (CollectionUtils.isNotEmpty(missingLangCodes)) {
            String missingCodes = String.join(", ", missingLangCodes);
            log.warn("Missing languages: {}", missingCodes);
            throw new FieldValidationException(validateField, "form.common.missingLanguages", missingCodes);
        }
    }

    /**
     * 获取已提交的语言代码列表
     * 从翻译数据中提取所有语言代码
     *
     * @param translations        翻译数据列表
     * @param getLanguageCodeFunc 获取语言代码的函数
     * @param <T>                 翻译数据类型
     * @return 语言代码列表
     */
    private static <T> List<String> getSubmittedLanguageCodes(List<T> translations, Function<T, String> getLanguageCodeFunc) {
        return translations.stream()
                .map(getLanguageCodeFunc)
                .toList();
    }

    /**
     * 找出无效的语言
     * 找出系统在提交列表中无效的语言代码
     *
     * @param submittedLangCodes 已提交的语言代码列表
     * @param supportedLangCodes 系统支持的语言代码列表
     * @return 无效的语言代码列表
     */
    private static Set<String> invalidLanguages(List<String> submittedLangCodes, Set<String> supportedLangCodes) {
        return submittedLangCodes.stream()
                .filter(code -> !supportedLangCodes.contains(code))
                .collect(Collectors.toSet());
    }

    /**
     * 找出缺失的语言
     * 找出系统支持但未在提交列表中的语言代码
     *
     * @param submittedLangCodes 已提交的语言代码列表
     * @param supportedLangCodes 系统支持的语言代码列表
     * @return 缺失的语言代码列表
     */
    private static Set<String> findMissingLanguages(List<String> submittedLangCodes, Set<String> supportedLangCodes) {
        return supportedLangCodes.stream()
                .filter(code -> !submittedLangCodes.contains(code))
                .collect(Collectors.toSet());
    }

    /**
     * 找出重复的元素
     * 从给定的元素列表中找出重复的元素
     *
     * @param items 元素列表
     * @return 重复元素列表
     */
    private static Set<String> findDuplicates(List<String> items) {
        Set<String> seen = new HashSet<>();
        return items.stream()
                .filter(item -> !seen.add(item))
                .collect(Collectors.toSet());
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private TranslationUtils() {
    }

} 
