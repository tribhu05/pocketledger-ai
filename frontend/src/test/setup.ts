import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock window.scrollTo for jsdom
window.scrollTo = vi.fn();
